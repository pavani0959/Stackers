from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from config import get_settings
from database import get_db
from services.profile_service import get_user_or_raise

settings = get_settings()

router = APIRouter(
    prefix="/api/wardrobe",
    tags=["wardrobe"],
)


@router.get(
    "",
    response_model=list[schemas.WardrobeItemResponse],
)
def list_wardrobe_items(
    db: Session = Depends(get_db),
):
    return (
        db.query(models.WardrobeItem)
        .filter(
            models.WardrobeItem.user_id
            == settings.demo_user_id,
            models.WardrobeItem.is_active.is_(True),
        )
        .order_by(
            models.WardrobeItem.created_at.desc()
        )
        .all()
    )


@router.post(
    "",
    response_model=schemas.WardrobeItemResponse,
    status_code=201,
)
def create_wardrobe_item(
    payload: schemas.WardrobeItemCreate,
    db: Session = Depends(get_db),
):
    get_user_or_raise(
        db,
        settings.demo_user_id,
    )

    item = models.WardrobeItem(
        user_id=settings.demo_user_id,
        **payload.model_dump(),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item