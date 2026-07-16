from routers.decisions import router as decisions_router
from routers.events import router as events_router
from routers.profile import router as profile_router
from routers.wardrobe import router as wardrobe_router
import json
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from config import get_settings
from database import get_db
from errors import (
    AppError,
    NotFoundError,
    app_error_handler,
    http_exception_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from ml import (
    blend_dna,
    calculate_dna_ml,
    find_twins,
    generate_outfit_nlp,
    muse_chat_response,
)

settings = get_settings()

app = FastAPI(title="Myntra Identity API")

app.include_router(profile_router)
app.include_router(events_router)
app.include_router(wardrobe_router)
app.include_router(decisions_router)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def product_to_dict(product: models.Product) -> dict:
    """Convert one ORM product into the API shape without mutating the ORM row."""
    def _to_list(val):
        if not val:
            return []
        if isinstance(val, list):
            return val
        return [v.strip() for v in val.split(",") if v.strip()]

    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "price": product.price,
        "originalPrice": product.originalPrice,
        "image": product.image,
        "tags": _to_list(product.tags),
        "occasions": _to_list(product.occasions),
        "budgetTier": product.budgetTier,
        "season": product.season,
    }


@app.get("/")
def read_root():
    return {"message": "Welcome to Myntra Identity API"}


@app.get("/api/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}


@app.get("/api/products", response_model=List[schemas.ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    q: str = "",
    category: str = "",
    min_price: int = 0,
    max_price: int = 0,
    db: Session = Depends(get_db),
):
    from sqlalchemy import or_, func
    query = db.query(models.Product)

    if q:
        q_lower = q.lower().strip()
        query = query.filter(
            or_(
                func.lower(models.Product.name).contains(q_lower),
                func.lower(models.Product.brand).contains(q_lower),
            )
        )

    if category:
        query = query.filter(
            func.lower(models.Product.category) == category.lower()
        )

    if min_price > 0:
        query = query.filter(models.Product.price >= min_price)

    if max_price > 0:
        query = query.filter(models.Product.price <= max_price)

    products = query.offset(skip).limit(limit).all()
    return [product_to_dict(product) for product in products]

@app.get(
    "/api/products/{product_id}",
    response_model=schemas.ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id)
        .first()
    )

    if not product:
        raise NotFoundError("Product not found")

    return product_to_dict(product)


@app.post("/api/dna/calculate")
def calculate_dna(request: schemas.DNARequest):
    return calculate_dna_ml(request.tags)







@app.post(
    "/api/recommend/reverse",
    response_model=schemas.ReverseShoppingResponse,
)
def reverse_shopping(
    request: schemas.ReverseShoppingRequest,
    db: Session = Depends(get_db),
):
    products = [product_to_dict(product) for product in db.query(models.Product).all()]
    result = generate_outfit_nlp(
        request.prompt,
        request.user_profile.model_dump(),
        products,
    )

    # ---- Persist as a RecommendationSession ----
    try:
        user = db.query(models.User).filter(
            models.User.id == settings.demo_user_id
        ).first()
        if user:
            # Resolve latest style profile
            sp = (
                db.query(models.StyleProfile)
                .filter(models.StyleProfile.user_id == user.id)
                .order_by(models.StyleProfile.version.desc())
                .first()
            )
            session = models.RecommendationSession(
                user_id=user.id,
                style_profile_id=sp.id if sp else None,
                profile_version=sp.version if sp else 0,
                profile_snapshot=request.user_profile.model_dump(),
                context_snapshot={
                    "prompt": request.prompt,
                    "budget_source": result.get("budget_source"),
                    "budget_limit": result.get("budget_limit"),
                },
                session_type="reverse",
                raw_prompt=request.prompt,
                parsed_intent=result.get("parsed_intent", {}),
                model_version="reverse-v1.0.0",
            )
            db.add(session)
            db.flush()  # get session.id

            for rank, outfit in enumerate(result.get("outfits", []), start=1):
                # Store one RecommendationItem per outfit using the first product as anchor
                first_item = outfit.get("items", [{}])[0]
                first_product_id = first_item.get("id")
                if not first_product_id:
                    continue
                rec_item = models.RecommendationItem(
                    session_id=session.id,
                    product_id=first_product_id,
                    rank=rank,
                    overall_score=float(outfit["score"]),
                    product_snapshot={
                        "outfit_label": outfit.get("label", ""),
                        "total_price": outfit.get("total", 0),
                        "item_ids": [i["id"] for i in outfit.get("items", [])],
                    },
                    score_breakdown=outfit.get("breakdown", {}),
                    explanation={"why": outfit.get("why", [])},
                    evidence_sources={},
                    regret_signals=[],
                    warning={},
                )
                db.add(rec_item)

            db.commit()
            # Overwrite the ephemeral UUID with the real DB session id
            result["session_id"] = str(session.id)
    except Exception:
        db.rollback()
        # Non-fatal: result is still returned even if persistence fails

    return result


@app.post("/api/community/twins")
def get_twins(request: schemas.FeedRequest, db: Session = Depends(get_db)):
    profiles = db.query(models.CommunityProfile).all()
    scored_twins = find_twins(request.user_profile.dna, profiles)

    response = []
    for scored_twin in scored_twins:
        profile = scored_twin["profile"]
        response.append(
            {
                "id": profile.id,
                "name": profile.name,
                "handle": profile.handle,
                "avatar": profile.avatar,
                "role": profile.role,
                "dna": json.loads(profile.dna_json),
                "dna_label": profile.dna_label,
                "recent_purchases": json.loads(profile.recent_purchases),
                "match_percentage": scored_twin["match"],
            }
        )

    return response


@app.post("/api/dna/blend")
def blend_user_dna(request: schemas.BlendRequest):
    merged = blend_dna(
        request.user_profile.dna,
        request.creator_dna,
        request.blend_percentage,
    )
    return {"merged_dna": merged}


@app.post("/api/muse/chat", response_model=schemas.MuseResponse)
def muse_chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    products = [product_to_dict(product) for product in db.query(models.Product).all()]
    return muse_chat_response(
        request.message,
        request.user_profile.model_dump(),
        products,
    )
