from datetime import datetime, timezone
import random

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from config import get_settings
from database import get_db
from services.profile_service import get_user_or_raise
from services.dna_service import DNAService
from services.regret_signal_service import RegretSignalService

settings = get_settings()

router = APIRouter(
    prefix="/api",
    tags=["memory"],
)


@router.post(
    "/events",
    response_model=schemas.UserEventResponse,
    status_code=201,
)
def create_event(
    payload: schemas.UserEventCreate,
    db: Session = Depends(get_db),
):
    get_user_or_raise(
        db,
        settings.demo_user_id,
    )

    event = models.UserEvent(
        user_id=settings.demo_user_id,
        event_type=payload.event_type.value,
        product_id=payload.product_id,
        wardrobe_item_id=payload.wardrobe_item_id,
        recommendation_item_id=payload.recommendation_item_id,
        event_metadata=payload.metadata,
        occurred_at=payload.occurred_at or datetime.now(timezone.utc),
    )
    db.add(event)
    
    # Evolve DNA if this event is associated with a product
    if payload.product_id:
        product = db.query(models.Product).filter(models.Product.id == payload.product_id).first()
        if product:
            # We map some tags to traits to fake a vector if actual dna vector isn't on product
            # In a real system, products would have pre-computed vectors.
            item_vector = {}
            for tag in product.tags:
                tag = tag.lower()
                if "minimal" in tag: item_vector["minimalist"] = 0.5
                if "street" in tag: item_vector["streetwear"] = 0.5
                if "casual" in tag: item_vector["campusCasual"] = 0.5
                if "luxury" in tag: item_vector["quietLuxury"] = 0.5
                if "y2k" in tag: item_vector["y2k"] = 0.5
            
            if item_vector:
                dna_service = DNAService(db)
                dna_service.evolve_dna_from_event(
                    user_id=settings.demo_user_id,
                    event_type=payload.event_type.value,
                    item_vector=item_vector
                )

    db.commit()
    db.refresh(event)
    return event


@router.get(
    "/events",
    response_model=list[schemas.UserEventResponse],
)
def list_events(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.UserEvent)
        .filter(models.UserEvent.user_id == settings.demo_user_id)
        .order_by(models.UserEvent.occurred_at.desc())
        .limit(limit)
        .all()
    )


@router.get(
    "/memory/timeline",
)
def get_timeline(db: Session = Depends(get_db)):
    """Returns a rich timeline merging events and their related product metadata."""
    events = (
        db.query(models.UserEvent)
        .filter(models.UserEvent.user_id == settings.demo_user_id)
        .order_by(models.UserEvent.occurred_at.desc())
        .limit(30)
        .all()
    )
    
    timeline = []
    for ev in events:
        item = {
            "id": ev.id,
            "type": ev.event_type,
            "date": ev.occurred_at.isoformat(),
            "metadata": ev.event_metadata,
        }
        if ev.product_id:
            prod = db.query(models.Product).filter(models.Product.id == ev.product_id).first()
            if prod:
                item["product"] = {
                    "id": prod.id,
                    "name": prod.name,
                    "image": prod.image,
                    "price": prod.price,
                }
        timeline.append(item)
    return {"timeline": timeline}


@router.get(
    "/memory/regret-check/{product_id}",
)
def check_regret(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Checks a product against the user's history and wardrobe for potential regrets."""
    user = get_user_or_raise(db, settings.demo_user_id)
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    preferences = user.preferences
    
    # 1. Wardrobe duplicates
    wardrobe_items = db.query(models.WardrobeItem).filter(
        models.WardrobeItem.user_id == user.id,
        models.WardrobeItem.subcategory == product.subcategory,
        models.WardrobeItem.primary_colour == product.primary_colour,
    ).all()
    
    # 2. Return history
    returns = db.query(models.UserEvent).filter(
        models.UserEvent.user_id == user.id,
        models.UserEvent.event_type == "return",
        models.UserEvent.product_id.in_(
            db.query(models.Product.id).filter(models.Product.category == product.category)
        )
    ).count()

    score_breakdown = {
        "style": {"score": 80, "evidence": {}},
        "occasion": {"score": 80, "evidence": {}},
        "wardrobe": {
            "score": 50 if wardrobe_items else 90, 
            "evidence": {
                "duplicate_count": len(wardrobe_items),
                "subcategory": product.subcategory,
                "primary_colour": product.primary_colour
            }
        }
    }

    regret_svc = RegretSignalService()
    signals = regret_svc.generate(
        product=product,
        preferences=preferences,
        score_breakdown=score_breakdown,
        category_return_count=returns,
    )
    
    # Suggest alternatives (random similar category products not in wardrobe)
    alternatives = []
    if signals:
        alts = db.query(models.Product).filter(
            models.Product.category == product.category,
            models.Product.id != product.id
        ).limit(10).all()
        if alts:
            alt_prod = random.choice(alts)
            alternatives.append({
                "id": alt_prod.id,
                "name": alt_prod.name,
                "price": alt_prod.price,
                "image": alt_prod.image,
                "reason": "Different colour/style creates more wardrobe variety."
            })

    return {
        "product_id": product.id,
        "signals": signals,
        "alternatives": alternatives,
        "safe_to_buy": len(signals) == 0,
    }