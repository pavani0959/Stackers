from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

import models


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(
        self,
        user_id: int,
    ) -> models.User | None:
        return (
            self.db.query(models.User)
            .filter(models.User.id == user_id)
            .first()
        )

    def get_preferences(
        self,
        user_id: int,
    ) -> models.UserPreference:
        preferences = (
            self.db.query(models.UserPreference)
            .filter(
                models.UserPreference.user_id
                == user_id,
            )
            .first()
        )

        if preferences is None:
            preferences = models.UserPreference(
                user_id=user_id,
            )
            self.db.add(preferences)
            self.db.flush()

        return preferences

    def update_preferences(
        self,
        user_id: int,
        updates: dict[str, Any],
    ) -> models.UserPreference:
        preferences = self.get_preferences(
            user_id,
        )

        for field, value in updates.items():
            if hasattr(preferences, field):
                setattr(preferences, field, value)

        self.db.flush()
        return preferences

    def count_behavior_events(
        self,
        user_id: int,
    ) -> int:
        return (
            self.db.query(models.UserEvent)
            .filter(
                models.UserEvent.user_id
                == user_id,
            )
            .count()
        )

    def next_profile_version(
        self,
        user_id: int,
    ) -> int:
        current_version = (
            self.db.query(
                func.max(models.StyleProfile.version),
            )
            .filter(
                models.StyleProfile.user_id
                == user_id,
            )
            .scalar()
        )

        return int(current_version or 0) + 1

    def create_style_profile(
        self,
        *,
        user_id: int,
        version: int,
        dna: dict[str, float],
        identity: dict[str, Any],
        confidence: int,
        confidence_breakdown: dict[str, int],
        evidence: dict[str, int],
    ) -> models.StyleProfile:
        profile = models.StyleProfile(
            user_id=user_id,
            version=version,
            dna_vector=dna,
            primary_identity=identity["name"],
            secondary_identity=identity.get(
                "secondary",
            ),
            profile_confidence=confidence,
            identity=identity,
            confidence_breakdown=(
                confidence_breakdown
            ),
            evidence=evidence,
        )

        self.db.add(profile)
        self.db.flush()

        return profile