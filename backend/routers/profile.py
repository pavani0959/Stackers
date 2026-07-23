from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from services.dna_service import DNAService
import schemas
from database import get_db
from dependencies import get_current_user
from models import User
from services.profile_service import (
    create_style_profile,
    get_current_profile,
    update_identity,
    get_profile_payload,
    update_preferences,
)


router = APIRouter(
    prefix="/api/profile",
    tags=["profile"],
)

@router.post(
    "/dna/calculate",
    response_model=schemas.DNAProfileResponse,
)
def calculate_and_save_fashion_dna(
    payload: schemas.DNAProfileCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return DNAService(
            db,
        ).calculate_and_persist(
            user_id=current_user.id,
            answers=payload.answers,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=schemas.CurrentProfileResponse,
)
def get_current_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_profile_payload(
            db,
            current_user.id,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.put(
    "/preferences",
    response_model=schemas.UserPreferenceResponse,
    summary="Update current user preferences",
)
def save_preferences(
    payload: schemas.UserPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_preferences(
        db=db,
        user_id=current_user.id,
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
    current_user: User = Depends(get_current_user),
):
    return create_style_profile(
        db=db,
        user_id=current_user.id,
        payload=payload,
    )

@router.put(
    "/identity",
    response_model=schemas.UserResponse,
)
def save_identity(
    payload: schemas.UserIdentityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_identity(
        db,
        current_user.id,
        payload,
    )