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

    update_data = payload.model_dump(
        exclude_unset=True,
    )

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

    update_data = payload.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user

def get_profile_payload(
    db: Session,
    user_id: int,
) -> dict:
    user = (
        db.query(models.User)
        .filter(
            models.User.id == user_id,
        )
        .first()
    )

    if user is None:
        raise LookupError(
            f"User {user_id} was not found."
        )

    preferences = (
        db.query(models.UserPreference)
        .filter(
            models.UserPreference.user_id
            == user_id,
        )
        .first()
    )

    style_profile = (
        db.query(models.StyleProfile)
        .filter(
            models.StyleProfile.user_id
            == user_id,
        )
        .order_by(
            models.StyleProfile.version.desc(),
            models.StyleProfile.id.desc(),
        )
        .first()
    )

    user_payload = {
        "id": user.id,
        "name": user.name,
        "gender": user.gender,
        "age": user.age,
        "avatar_url": getattr(
            user,
            "avatar_url",
            None,
        ),
        "onboarding_completed": getattr(
            user,
            "onboarding_completed",
            False,
        ),
        "created_at": getattr(
            user,
            "created_at",
            None,
        ),
    }

    preferences_payload = None

    if preferences is not None:
        preferences_payload = {
            "budget_min": (
                preferences.budget_min
            ),
            "budget_max": (
                preferences.budget_max
            ),
            "budget_tier": (
                preferences.budget_tier
            ),
            "preferred_occasions": (
                preferences.preferred_occasions
                or []
            ),
            "preferred_colours": (
                preferences.preferred_colours
                or []
            ),
            "preferred_brands": (
                preferences.preferred_brands
                or []
            ),
            "preferred_aesthetics": (
                preferences.preferred_aesthetics
                or []
            ),
            "fit_preferences": (
                preferences.fit_preferences
                or []
            ),
            "comfort_priority": (
                preferences.comfort_priority
                if preferences.comfort_priority
                is not None
                else 0.5
            ),
            "trend_openness": (
                preferences.trend_openness
                if preferences.trend_openness
                is not None
                else 0.5
            ),
            "fashion_goal": getattr(
                preferences,
                "fashion_goal",
                None,
            ),
            "comfort_expression_balance": (
                getattr(
                    preferences,
                    "comfort_expression_balance",
                    None,
                )
                if getattr(
                    preferences,
                    "comfort_expression_balance",
                    None,
                )
                is not None
                else 0.5
            ),
            "occasion_priorities": (
                getattr(
                    preferences,
                    "occasion_priorities",
                    None,
                )
                or {}
            ),
        }

    style_profile_payload = None

    if style_profile is not None:
        style_profile_payload = {
            "profile_id": (
                style_profile.profile_id
            ),
            "version": (
                style_profile.version
            ),
            "dna_vector": (
                style_profile.dna_vector
                or {}
            ),
            "primary_identity": (
                style_profile.primary_identity
            ),
            "secondary_identity": (
                style_profile.secondary_identity
            ),
            "profile_confidence": (
                style_profile.profile_confidence
            ),
            "identity": (
                style_profile.identity
                or {}
            ),
            "confidence_breakdown": (
                style_profile.confidence_breakdown
                or {}
            ),
            "evidence": (
                style_profile.evidence
                or {}
            ),
        }

    return {
        "user": user_payload,
        "preferences": preferences_payload,
        "style_profile": style_profile_payload,
    }