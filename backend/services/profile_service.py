from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
from errors import NotFoundError


def get_user_or_raise(
    db: Session,
    user_id: int,
) -> models.User:
    user = db.get(models.User, user_id)

    if user is None:
        raise NotFoundError("User not found")

    return user


def get_latest_style_profile(
    db: Session,
    user_id: int,
) -> models.StyleProfile | None:
    return (
        db.query(models.StyleProfile)
        .filter(models.StyleProfile.user_id == user_id)
        .order_by(models.StyleProfile.version.desc())
        .first()
    )


def get_current_profile(
    db: Session,
    user_id: int,
) -> dict:
    user = get_user_or_raise(db, user_id)

    return {
        "user": user,
        "preferences": user.preferences,
        "style_profile": get_latest_style_profile(
            db,
            user_id,
        ),
    }


def update_preferences(
    db: Session,
    user_id: int,
    payload: schemas.UserPreferenceUpdate,
) -> models.UserPreference:
    user = get_user_or_raise(db, user_id)

    preference = user.preferences

    if preference is None:
        preference = models.UserPreference(
            user_id=user.id,
        )
        db.add(preference)

    update_data = payload.model_dump()

    for field, value in update_data.items():
        setattr(preference, field, value)

    user.onboarding_completed = True

    db.commit()
    db.refresh(preference)

    return preference


def normalize_dna(
    dna_vector: dict[str, float],
) -> dict[str, float]:
    total = sum(dna_vector.values())

    normalized = {
        label: round((score / total) * 100, 2)
        for label, score in dna_vector.items()
    }

    difference = round(
        100 - sum(normalized.values()),
        2,
    )

    largest_label = max(
        normalized,
        key=normalized.get,
    )

    normalized[largest_label] = round(
        normalized[largest_label] + difference,
        2,
    )

    return normalized


def create_style_profile(
    db: Session,
    user_id: int,
    payload: schemas.StyleProfileCreate,
) -> models.StyleProfile:
    get_user_or_raise(db, user_id)

    current_version = (
        db.query(
            func.max(models.StyleProfile.version)
        )
        .filter(models.StyleProfile.user_id == user_id)
        .scalar()
    )

    next_version = (current_version or 0) + 1

    style_profile = models.StyleProfile(
        user_id=user_id,
        version=next_version,
        dna_vector=normalize_dna(payload.dna_vector),
        primary_identity=payload.primary_identity,
        secondary_identity=payload.secondary_identity,
        profile_confidence=payload.profile_confidence,
        source=payload.source,
        model_version=payload.model_version,
    )

    db.add(style_profile)
    db.commit()
    db.refresh(style_profile)

    return style_profile

def update_identity(
    db: Session,
    user_id: int,
    payload: schemas.UserIdentityUpdate,
) -> models.User:
    user = get_user_or_raise(
        db,
        user_id,
    )

    update_data = payload.model_dump()

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user