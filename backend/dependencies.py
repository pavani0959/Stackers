from fastapi import (
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from config import get_settings
from database import get_db
from models import User


def get_current_user(
    db: Session = Depends(get_db),
) -> User:
    """
    Return the server-controlled current user.

    The project currently uses DEMO_USER_ID until
    authentication is introduced. API clients must
    not provide or select the current user.
    """
    settings = get_settings()

    user = db.get(
        User,
        settings.demo_user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "The configured current user "
                "does not exist."
            ),
        )

    return user
