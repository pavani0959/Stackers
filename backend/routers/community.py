from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

import schemas
from database import get_db
from dependencies import get_current_user
from models import User
from repositories.style_twin_repository import (
    StyleTwinRepository,
)
from services.style_twin_service import (
    StyleTwinService,
)


router = APIRouter(
    prefix="/api/community",
    tags=["community"],
)


@router.get(
    "/twins",
    response_model=(
        schemas.StyleTwinCollectionResponse
    ),
)
def get_style_twins(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    repository = StyleTwinRepository(
        db,
    )

    service = StyleTwinService(
        repository,
    )

    try:
        return service.find_twins(
            current_user.id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error


@router.get(
    "/profiles",
    response_model=list[
        schemas.CommunityProfileCard
    ],
)
def get_community_profiles(
    db: Session = Depends(get_db),
):
    """
    Presentation-only creator/community profiles.

    These rows are deliberately separate from the
    evidence-backed Style Twin endpoint.
    """
    repository = StyleTwinRepository(
        db,
    )

    service = StyleTwinService(
        repository,
    )

    return service.list_static_profiles()
