from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

import models


@dataclass(
    frozen=True,
    slots=True,
)
class StyleTwinRecord:
    user: models.User
    preference: models.UserPreference | None
    profile: models.StyleProfile


class StyleTwinRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def get_latest_profile(
        self,
        user_id: int,
    ) -> models.StyleProfile | None:
        return (
            self.db.query(
                models.StyleProfile,
            )
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

    def get_preference(
        self,
        user_id: int,
    ) -> models.UserPreference | None:
        return (
            self.db.query(
                models.UserPreference,
            )
            .filter(
                models.UserPreference.user_id
                == user_id,
            )
            .first()
        )

    def get_candidate_records(
        self,
        current_user_id: int,
    ) -> list[StyleTwinRecord]:
        """
        Load one latest StyleProfile per seeded user.

        CommunityProfile is intentionally not used
        here. Those rows remain presentation-only
        creator/community cards.
        """
        profiles = (
            self.db.query(
                models.StyleProfile,
            )
            .filter(
                models.StyleProfile.user_id
                != current_user_id,
            )
            .order_by(
                models.StyleProfile.user_id.asc(),
                models.StyleProfile.version.desc(),
                models.StyleProfile.id.desc(),
            )
            .all()
        )

        latest_profiles: dict[
            int,
            models.StyleProfile,
        ] = {}

        for profile in profiles:
            if (
                profile.user_id
                not in latest_profiles
            ):
                latest_profiles[
                    profile.user_id
                ] = profile

        if not latest_profiles:
            return []

        candidate_ids = sorted(
            latest_profiles,
        )

        user_query = (
            self.db.query(models.User)
            .filter(
                models.User.id.in_(
                    candidate_ids,
                ),
                models.User.id
                != current_user_id,
            )
        )

        # Synthetic demo users have seed_key in
        # the current data model. Keep this check
        # defensive so the repository remains
        # compatible with older local databases.
        if hasattr(
            models.User,
            "seed_key",
        ):
            user_query = user_query.filter(
                models.User.seed_key.is_not(
                    None,
                ),
            )

        users = user_query.all()

        preferences = (
            self.db.query(
                models.UserPreference,
            )
            .filter(
                models.UserPreference.user_id.in_(
                    candidate_ids,
                ),
            )
            .all()
        )

        preference_by_user = {
            preference.user_id: preference
            for preference in preferences
        }

        records = [
            StyleTwinRecord(
                user=user,
                preference=preference_by_user.get(
                    user.id,
                ),
                profile=latest_profiles[user.id],
            )
            for user in users
            if user.id in latest_profiles
        ]

        return sorted(
            records,
            key=lambda record: record.user.id,
        )

    def get_cohort_events(
        self,
        user_ids: list[int],
    ) -> list[models.UserEvent]:
        if not user_ids:
            return []

        return (
            self.db.query(
                models.UserEvent,
            )
            .filter(
                models.UserEvent.user_id.in_(
                    user_ids,
                ),
                models.UserEvent.product_id.is_not(
                    None,
                ),
                models.UserEvent.event_type.in_(
                    (
                        "keep",
                        "wear",
                        "return",
                    ),
                ),
            )
            .order_by(
                models.UserEvent.product_id.asc(),
                models.UserEvent.occurred_at.asc(),
                models.UserEvent.id.asc(),
            )
            .all()
        )

    def get_static_community_profiles(
        self,
    ) -> list[models.CommunityProfile]:
        """
        Static CommunityProfile rows may still be
        used for creator/community presentation.

        They must never be used as Style Twins.
        """
        return (
            self.db.query(
                models.CommunityProfile,
            )
            .order_by(
                models.CommunityProfile.id.asc(),
            )
            .all()
        )
