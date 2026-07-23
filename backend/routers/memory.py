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
from services.memory_service import (
    MemoryService,
)


router = APIRouter(
    prefix="/api/memory",
    tags=["memory"],
)


@router.post(
    "/checkout",
    response_model=schemas.CheckoutResponse,
)
def checkout(
    payload: schemas.CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    service = MemoryService(db)

    try:
        response = service.checkout(
            user_id=current_user.id,
            payload=payload,
        )

        db.commit()
        return response

    except LookupError as error:
        db.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception:
        db.rollback()
        raise


@router.post(
    "/items/{wardrobe_item_id}/keep",
    response_model=schemas.MemoryActionResponse,
)
def keep_item(
    wardrobe_item_id: int,
    payload: schemas.MemoryActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    service = MemoryService(db)

    try:
        response = service.record_action(
            user_id=current_user.id,
            wardrobe_item_id=wardrobe_item_id,
            event_type="keep",
            reason=payload.reason,
        )

        db.commit()
        return response

    except LookupError as error:
        db.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception:
        db.rollback()
        raise


@router.post(
    "/items/{wardrobe_item_id}/return",
    response_model=schemas.MemoryActionResponse,
)
def return_item(
    wardrobe_item_id: int,
    payload: schemas.MemoryActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    service = MemoryService(db)

    try:
        response = service.record_action(
            user_id=current_user.id,
            wardrobe_item_id=wardrobe_item_id,
            event_type="return",
            reason=payload.reason,
        )

        db.commit()
        return response

    except LookupError as error:
        db.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception:
        db.rollback()
        raise
