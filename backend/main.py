from routers.decisions import router as decisions_router
from routers.events import router as events_router
from routers.profile import router as profile_router
from routers.wardrobe import router as wardrobe_router
import json
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
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

from services.intent_parser import extract_intent
from services.outfit_builder import build_outfits
from services.decision_score_calculator import DecisionScoreCalculator

from observability import (
    request_observability_middleware,
)

settings = get_settings()

from routers.memory import router as memory_router

from routers.community import router as community_router

app = FastAPI(title="Myntra Identity API")

app.middleware("http")(
    request_observability_middleware
)

app.include_router(profile_router)
app.include_router(events_router)
app.include_router(wardrobe_router)
app.include_router(decisions_router)
app.include_router(memory_router)
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


def product_to_dict(
    product: models.Product,
) -> dict:
    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "brand": product.brand,
        "description": product.description,
        "price": product.price,
        "originalPrice": product.originalPrice,
        "image": product.image,
        "category": product.category,
        "subcategory": product.subcategory,
        "primary_colour": product.primary_colour,
        "gender_segment": product.gender_segment,
        "tags": list(product.tags or []),
        "occasions": list(product.occasions or []),
        "sizes": list(product.sizes or []),
        "budgetTier": product.budgetTier,
        "season": product.season,
        "stock_quantity": product.stock_quantity,
        "is_active": product.is_active,
    }



app.include_router(community_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Myntra Identity API"}


@app.get("/api/health/live")
@app.get("/health/live")
def health_live():
    return {"status": "ok", "environment": settings.environment}


@app.get("/api/health/ready")
@app.get("/health/ready")
def health_ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unreachable")


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






@app.post(
    "/api/recommend/reverse",
    response_model=schemas.ReverseShoppingResponse,
)
def reverse_shopping(
    request: schemas.ReverseShoppingRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(
            models.User.id
            == settings.demo_user_id
        )
        .first()
    )

    if user is None:
        raise NotFoundError(
            "Demo user was not found."
        )

    style_profile = (
        db.query(models.StyleProfile)
        .filter(
            models.StyleProfile.user_id
            == user.id
        )
        .order_by(
            models.StyleProfile.version.desc()
        )
        .first()
    )

    if style_profile is None:
        raise HTTPException(
            status_code=409,
            detail=(
                "Complete your Fashion DNA "
                "before requesting outfits."
            ),
        )

    preferences = (
        db.query(models.UserPreference)
        .filter(
            models.UserPreference.user_id
            == user.id
        )
        .first()
    )

    user_profile = {
        "id": user.id,
        "name": user.name or "",
        "dna": dict(
            style_profile.dna_vector or {}
        ),
        "identityName": (
            style_profile.primary_identity
            or ""
        ),
        "profileConfidence": (
            style_profile.profile_confidence
            or 0
        ),
        "budget": (
            preferences.budget_tier
            if (
                preferences is not None
                and preferences.budget_tier
            )
            else "campus-casual"
        ),
        "budgetMin": (
            preferences.budget_min
            if preferences is not None
            else None
        ),
        "budgetMax": (
            preferences.budget_max
            if preferences is not None
            else None
        ),
        "occasions": (
            list(
                preferences.preferred_occasions
                or []
            )
            if preferences is not None
            else []
        ),
        "colours": (
            list(
                preferences.preferred_colours
                or []
            )
            if preferences is not None
            else []
        ),
        "brands": (
            list(
                preferences.preferred_brands
                or []
            )
            if preferences is not None
            else []
        ),
        "aesthetics": (
            list(
                preferences.preferred_aesthetics
                or []
            )
            if preferences is not None
            else []
        ),
        "purchaseMemory": [],
    }

    parsed_intent = extract_intent(request.prompt)
    budget_source = "prompt" if parsed_intent.get("budget_total") else "profile"
    
    # We use a fallback logic similar to PROFILE_BUDGET_LIMITS
    budget_tier = preferences.budget_tier if preferences and preferences.budget_tier else "campus-casual"
    profile_budget_limits = {
        "budget-explorer": 500,
        "smart-spender": 1500,
        "campus-casual": 3000,
        "style-investor": 7000,
        "luxury-seeker": 15000,
    }
    fallback_budget = profile_budget_limits.get(budget_tier, 3000)
    budget_limit = parsed_intent.get("budget_total") or fallback_budget

    wardrobe_items = db.query(models.WardrobeItem).filter(
        models.WardrobeItem.user_id == user.id,
        models.WardrobeItem.is_active.is_(True)
    ).all()
    
    products_db = db.query(models.Product).filter(models.Product.is_active.is_(True)).all()
    
    calculator = DecisionScoreCalculator()
    scored_products = []
    
    context = {"occasion": parsed_intent.get("occasion")}
    for product in products_db:
        calc_result = calculator.calculate(
            style_profile=style_profile,
            preferences=preferences,
            product=product,
            wardrobe_items=wardrobe_items,
            context=context,
        )
        prod_dict = product_to_dict(product)
        prod_dict["final_score"] = calc_result["overall_score"]
        prod_dict["breakdown"] = calc_result["score_breakdown"]
        prod_dict["category"] = product.category or ""
        scored_products.append(prod_dict)

    builder_result = build_outfits(
        intent=parsed_intent,
        scored_products=scored_products,
        fallback_budget=fallback_budget,
    )

    if builder_result.get("error") and not builder_result.get("outfits"):
        return {
            "prompt": request.prompt,
            "budget_limit": budget_limit,
            "budget_source": budget_source,
            "matched_terms": [],
            "within_budget": False,
            "message": builder_result["error"],
            "outfits": [],
            "closest_total": None,
            "closest_over_by": None,
            "reused_items": False,
            "parsed_intent": parsed_intent,
            "session_id": builder_result.get("session_id"),
        }

    response_outfits = []
    for index, candidate in enumerate(builder_result.get("outfits", []), start=1):
        items = []
        for raw_item in candidate["items"]:
            items.append({
                "id":        raw_item.get("id"),
                "name":      raw_item.get("name", ""),
                "brand":     raw_item.get("brand", ""),
                "price":     raw_item.get("price", 0),
                "image":     raw_item.get("image", ""),
                "category":  raw_item.get("category", ""),
                "tags":      list(raw_item.get("tags") or []),
                "occasions": list(raw_item.get("occasions") or []),
            })
        label = candidate.get("label", f"Outfit {index}")
        response_outfits.append({
            "index":        index,
            "label":        label,
            "title":        label,
            "score":        candidate.get("overall_score", 0),
            "total":        candidate.get("total_price", 0),
            "within_budget": True,
            "breakdown":    candidate.get("breakdown", {}),
            "why":          candidate.get("why", []),
            "items":        items,
        })

    result = {
        "budget_source": budget_source,
        "budget_limit": budget_limit,
        "outfits": response_outfits,
        "parsed_intent": parsed_intent,
    }

    try:
        session = models.RecommendationSession(
            user_id=user.id,
            style_profile_id=style_profile.id,
            profile_version=(
                style_profile.version
            ),
            profile_snapshot={
                "profile_id": str(
                    getattr(
                        style_profile,
                        "profile_id",
                        style_profile.id,
                    )
                ),
                "version": (
                    style_profile.version
                ),
                "dna": dict(
                    style_profile.dna_vector
                    or {}
                ),
                "identity": (
                    style_profile.primary_identity
                    or ""
                ),
                "confidence": (
                    style_profile
                    .profile_confidence
                    or 0
                ),
                "budget": (
                    user_profile["budget"]
                ),
                "occasions": (
                    user_profile["occasions"]
                ),
            },
            context_snapshot={
                "prompt": request.prompt,
                "budget_source": (
                    result.get(
                        "budget_source"
                    )
                ),
                "budget_limit": (
                    result.get(
                        "budget_limit"
                    )
                ),
            },
            session_type="reverse",
            raw_prompt=request.prompt,
            parsed_intent=result.get(
                "parsed_intent",
                {},
            ),
            model_version=(
                "reverse-v1.0.0"
            ),
        )

        db.add(session)
        db.flush()

        for rank, outfit in enumerate(
            result.get("outfits", []),
            start=1,
        ):
            outfit_items = outfit.get(
                "items",
                [],
            )

            if not outfit_items:
                raise RuntimeError(
                    "Generated outfit contains "
                    "no products."
                )

            first_product_id = (
                outfit_items[0].get("id")
            )

            if first_product_id is None:
                raise RuntimeError(
                    "Generated outfit product "
                    "is missing its ID."
                )

            recommendation_item = (
                models.RecommendationItem(
                    session_id=session.id,
                    product_id=(
                        first_product_id
                    ),
                    rank=rank,
                    overall_score=float(
                        outfit.get(
                            "score",
                            0,
                        )
                    ),
                    product_snapshot={
                        "outfit_label": (
                            outfit.get(
                                "label",
                                "",
                            )
                        ),
                        "outfit_title": (
                            outfit.get(
                                "title",
                                "",
                            )
                        ),
                        "total_price": (
                            outfit.get(
                                "total",
                                0,
                            )
                        ),
                        "items": outfit_items,
                        "parsed_intent": (
                            result.get(
                                "parsed_intent",
                                {},
                            )
                        ),
                        "budget_limit": (
                            result.get(
                                "budget_limit"
                            )
                        ),
                    },
                    score_breakdown=(
                        outfit.get(
                            "breakdown",
                            {},
                        )
                    ),
                    explanation={
                        "why": outfit.get(
                            "why",
                            [],
                        ),
                    },
                    evidence_sources={
                        "profile_version": (
                            style_profile.version
                        ),
                        "catalogue": (
                            "database"
                        ),
                        "budget_source": (
                            result.get(
                                "budget_source"
                            )
                        ),
                    },
                    regret_signals=[],
                    warning={},
                )
            )

            db.add(recommendation_item)
            db.flush()

            outfit["recommendation_item_id"] = (
                recommendation_item.id
            )

            outfit["snapshot_id"] = str(
                recommendation_item.snapshot_id
            )

        db.commit()

        # Merge response layout for the route return
        return {
            "prompt": request.prompt,
            "budget_limit": budget_limit,
            "budget_source": budget_source,
            "matched_terms": [],
            "within_budget": True,
            "message": f"Built {len(response_outfits)} complete outfit(s) within ₹{budget_limit:,}.",
            "outfits": response_outfits,
            "closest_total": None,
            "closest_over_by": None,
            "reused_items": False,
            "parsed_intent": parsed_intent,
            "session_id": str(session.id),
        }
    except Exception:
        db.rollback()
        raise


@app.post("/api/dna/blend")
def blend_user_dna(request: schemas.BlendRequest, db: Session = Depends(get_db)):
    from services.dna_service import DNAService
    merged = DNAService(db).blend_with_creator(
        request.user_profile.dna,
        request.creator_dna,
        request.blend_percentage,
    )
    return {"merged_dna": merged}


@app.post("/api/muse/chat", response_model=schemas.MuseResponse)
def muse_chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    from services.muse_service import MuseService
    service = MuseService(db)
    # the frontend currently passes request.user_profile, but we only need user_id to fetch from db.
    # since ChatRequest.user_profile doesn't have an ID easily, we will use settings.demo_user_id 
    # to emulate logged-in user in this demo app.
    return service.chat(request.message, settings.demo_user_id)


# ---------------------------------------------------------------------------
# System health
# ---------------------------------------------------------------------------

@app.get(
    "/health",
    tags=["system"],
    summary="Check API health",
)
async def health_check() -> dict[str, str]:
    """Return a lightweight process health response."""
    return {
        "status": "ok",
    }

