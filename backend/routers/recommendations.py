from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from config import get_settings
from database import get_db
from errors import NotFoundError
from services.profile_service import (
    get_latest_style_profile,
    get_user_or_raise,
)

settings = get_settings()

router = APIRouter(
    prefix="/api/recommendation-sessions",
    tags=["recommendation sessions"],
)


@router.post(
    "",
    status_code=201,
)
def create_recommendation_session(
    payload: schemas.RecommendationSessionCreate,
    db: Session = Depends(get_db),
):
    get_user_or_raise(
        db,
        settings.demo_user_id,
    )

    latest_profile = get_latest_style_profile(
        db,
        settings.demo_user_id,
    )

    session = models.RecommendationSession(
        user_id=settings.demo_user_id,
        style_profile_id=(
            latest_profile.id
            if latest_profile
            else None
        ),
        **payload.model_dump(),
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "id": session.id,
        "user_id": session.user_id,
        "style_profile_id": session.style_profile_id,
        "session_type": session.session_type,
        "raw_prompt": session.raw_prompt,
        "parsed_intent": session.parsed_intent,
        "model_version": session.model_version,
        "created_at": session.created_at,
    }


@router.post(
    "/{session_id}/items",
    status_code=201,
)
def create_recommendation_item(
    session_id: int,
    payload: schemas.RecommendationItemCreate,
    db: Session = Depends(get_db),
):
    session = db.get(
        models.RecommendationSession,
        session_id,
    )

    if (
        session is None
        or session.user_id != settings.demo_user_id
    ):
        raise NotFoundError(
            "Recommendation session not found"
        )

    product = db.get(
        models.Product,
        payload.product_id,
    )

    if product is None:
        raise NotFoundError("Product not found")

    item = models.RecommendationItem(
        session_id=session.id,
        **payload.model_dump(),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "session_id": item.session_id,
        "product_id": item.product_id,
        "rank": item.rank,
        "overall_score": item.overall_score,
        "score_breakdown": item.score_breakdown,
        "explanation": item.explanation,
        "warning": item.warning,
        "created_at": item.created_at,
    }