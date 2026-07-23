"""Password hashing and JWT token utilities."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    user_id: int,
    email: str,
) -> str:
    settings = get_settings()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expiry_minutes,
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm="HS256",
    )


def decode_access_token(token: str) -> dict | None:
    """Return the decoded payload or None if invalid/expired."""
    settings = get_settings()

    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=["HS256"],
        )
    except JWTError:
        return None
