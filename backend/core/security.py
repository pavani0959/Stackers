"""Password hashing and JWT token utilities."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
import bcrypt

from config import get_settings


def hash_password(plain: str) -> str:
    """Hash a password using bcrypt directly."""
    # bcrypt expects bytes, and we should manually truncate to 72 bytes to avoid errors
    plain_bytes = plain.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(plain_bytes, salt)
    return hashed_bytes.decode('ascii')


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password using bcrypt directly."""
    try:
        plain_bytes = plain.encode('utf-8')[:72]
        hashed_bytes = hashed.encode('ascii')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except (ValueError, TypeError):
        return False


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
