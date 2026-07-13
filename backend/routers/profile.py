from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import schemas
from config import get_settings
from database import get_db
from services.profile_service import (
    create_style_profile,
    get_current_profile,
    update_identity,
    update_preferences,
)

settings = get_settings()


router = APIRouter(
    prefix="/api/profile",
    tags=["profile"],
)


@router.get(
    "",
    response_model=schemas.CurrentProfileResponse,
    summary="Get current user profile",
)
def read_current_profile(
    db: Session = Depends(get_db),
):
    return get_current_profile(
        db=db,
        user_id=settings.demo_user_id,
    )


@router.put(
    "/preferences",
    response_model=schemas.UserPreferenceResponse,
    summary="Update current user preferences",
)
def save_preferences(
    payload: schemas.UserPreferenceUpdate,
    db: Session = Depends(get_db),
):
    return update_preferences(
        db=db,
        user_id=settings.demo_user_id,
        payload=payload,
    )


@router.post(
    "/dna",
    response_model=schemas.StyleProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Fashion DNA version",
)
def save_fashion_dna(
    payload: schemas.StyleProfileCreate,
    db: Session = Depends(get_db),
):
    return create_style_profile(
        db=db,
        user_id=settings.demo_user_id,
        payload=payload,
    )

@router.put(
    "/identity",
    response_model=schemas.UserResponse,
)
def save_identity(
    payload: schemas.UserIdentityUpdate,
    db: Session = Depends(get_db),
    settings: get_settings = Depends(get_settings),
):
    return update_identity(
        db,
        settings.demo_user_id,
        payload,
    )