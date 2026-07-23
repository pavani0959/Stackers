from fastapi import (
    Depends,
    Header,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from config import get_settings
from core.security import decode_access_token
from database import get_db
from models import User


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> User:
    """
    Return the current user.

    If a valid JWT Bearer token is present, use the
    authenticated user from the token.

    Otherwise, fall back to DEMO_USER_ID so existing
    tests and the demo environment keep working.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        payload = decode_access_token(token)

        if payload is not None:
            user_id = int(payload["sub"])
            user = db.get(User, user_id)

            if user is not None:
                return user

    # Fallback: use the configured demo user
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


def get_authenticated_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> User:
    """
    Strictly require a valid JWT token.

    This dependency rejects requests without a
    valid Bearer token — no demo fallback.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header.",
        )

    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    user_id = int(payload["sub"])
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    return user
