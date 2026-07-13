from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import models
import schemas
from config import get_settings
from database import get_db
from services.profile_service import get_user_or_raise

settings = get_settings()

router = APIRouter(
    prefix="/api/events",
    tags=["events"],
)


@router.post(
    "",
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
        recommendation_item_id=(
            payload.recommendation_item_id
        ),
        event_metadata=payload.metadata,
        occurred_at=(
            payload.occurred_at
            or datetime.now(timezone.utc)
        ),
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get(
    "",
    response_model=list[schemas.UserEventResponse],
)
def list_events(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.UserEvent)
        .filter(
            models.UserEvent.user_id
            == settings.demo_user_id
        )
        .order_by(
            models.UserEvent.occurred_at.desc()
        )
        .limit(limit)
        .all()
    )