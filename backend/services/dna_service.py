from decimal import Decimal, ROUND_FLOOR
from typing import Any

from sqlalchemy.orm import Session

from repositories.profile_repository import (
    ProfileRepository,
)
from schemas import DNAQuizAnswer
from services.feature_builder import (
    FeatureBundle,
    build_feature_bundle,
)


STYLE_LABELS = {
    "minimalist": "Minimalist",
    "streetwear": "Streetwear",
    "quietLuxury": "Quiet Luxury",
    "romantic": "Soft Romantic",
    "sporty": "Sporty",
    "y2k": "Y2K",
    "bohemian": "Bohemian",
    "campusCasual": "Campus Casual",
}


IDENTITY_DESCRIPTIONS = {
    "minimalist": (
        "Clean, versatile pieces and intentional "
        "styling form the centre of your wardrobe."
    ),
    "streetwear": (
        "Relaxed silhouettes, expressive layers and "
        "urban details define your style."
    ),
    "quietLuxury": (
        "Polished essentials, refined colours and "
        "quality-focused choices define your identity."
    ),
    "romantic": (
        "Soft colours, graceful shapes and expressive "
        "details bring your wardrobe to life."
    ),
    "sporty": (
        "Comfort, movement and functional styling "
        "drive your fashion choices."
    ),
    "y2k": (
        "Bold combinations, nostalgic details and "
        "trend-led expression shape your wardrobe."
    ),
    "bohemian": (
        "Natural colours, relaxed layers and artistic "
        "details define your style."
    ),
    "campusCasual": (
        "Comfortable, practical and versatile outfits "
        "support your everyday campus life."
    ),
}


def normalize_dna(
    scores: dict[str, float],
) -> dict[str, float]:
    positive_scores = {
        key: Decimal(str(value))
        for key, value in scores.items()
        if value > 0
    }

    total = sum(positive_scores.values())

    if total <= 0:
        raise ValueError(
            "DNA scores must contain a positive total."
        )

    exact_basis_points = {
        key: (
            value
            * Decimal("10000")
            / total
        )
        for key, value in positive_scores.items()
    }

    floor_basis_points = {
        key: int(
            value.to_integral_value(
                rounding=ROUND_FLOOR,
            ),
        )
        for key, value in (
            exact_basis_points.items()
        )
    }

    remaining = (
        10000
        - sum(floor_basis_points.values())
    )

    remainder_order = sorted(
        exact_basis_points,
        key=lambda key: (
            exact_basis_points[key]
            - floor_basis_points[key],
            key,
        ),
        reverse=True,
    )

    for key in remainder_order[:remaining]:
        floor_basis_points[key] += 1

    normalized = {
        key: value / 100
        for key, value in (
            floor_basis_points.items()
        )
    }

    if round(sum(normalized.values()), 2) != 100:
        raise RuntimeError(
            "Normalized DNA did not total 100."
        )

    return dict(
        sorted(
            normalized.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        ),
    )


def build_identity(
    dna: dict[str, float],
) -> dict[str, Any]:
    ordered = sorted(
        dna.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    )

    primary = ordered[0][0]
    secondary = (
        ordered[1][0]
        if len(ordered) > 1
        else None
    )

    primary_label = STYLE_LABELS.get(
        primary,
        primary,
    )

    secondary_label = (
        STYLE_LABELS.get(
            secondary,
            secondary,
        )
        if secondary
        else None
    )

    name = (
        f"{primary_label} {secondary_label}"
        if secondary_label
        else primary_label
    )

    return {
        "name": name,
        "description": (
            IDENTITY_DESCRIPTIONS.get(
                primary,
                "Your Fashion DNA reflects a "
                "distinctive and evolving style.",
            )
        ),
        "primary": primary,
        "secondary": secondary,
    }


def calculate_confidence(
    *,
    dna: dict[str, float],
    preferences: Any,
    quiz_answer_count: int,
    behavior_event_count: int,
) -> tuple[int, dict[str, int]]:
    quiz_score = round(
        min(
            quiz_answer_count / 8,
            1,
        )
        * 40,
    )

    values = sorted(
        dna.values(),
        reverse=True,
    )

    top = values[0] if values else 0
    second = values[1] if len(values) > 1 else 0

    normalized_margin = (
        (top - second) / top
        if top > 0
        else 0
    )

    consistency_score = round(
        min(
            max(normalized_margin, 0),
            1,
        )
        * 25,
    )

    preference_groups = [
        bool(
            preferences.preferred_aesthetics
        ),
        bool(preferences.preferred_brands),
        bool(preferences.fit_preferences),
        bool(preferences.preferred_colours),
        bool(preferences.occasion_priorities),
        bool(preferences.fashion_goal),
    ]

    populated_groups = sum(
        preference_groups,
    )

    preference_score = round(
        min(
            populated_groups
            / len(preference_groups),
            1,
        )
        * 20,
    )

    behavior_score = round(
        min(
            behavior_event_count / 20,
            1,
        )
        * 15,
    )

    breakdown = {
        "quiz_completeness": quiz_score,
        "answer_consistency": (
            consistency_score
        ),
        "preference_coverage": (
            preference_score
        ),
        "behavior_evidence": behavior_score,
    }

    return sum(breakdown.values()), breakdown


class DNAService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProfileRepository(db)

    def calculate_and_persist(
        self,
        *,
        user_id: int,
        answers: list[DNAQuizAnswer],
    ) -> dict[str, Any]:
        user = self.repository.get_user(
            user_id,
        )

        if user is None:
            raise LookupError(
                f"User {user_id} was not found."
            )

        bundle: FeatureBundle = (
            build_feature_bundle(answers)
        )

        preferences = (
            self.repository.update_preferences(
                user_id,
                bundle.preference_updates,
            )
        )

        dna = normalize_dna(bundle.scores)
        identity = build_identity(dna)

        behavior_event_count = (
            self.repository.count_behavior_events(
                user_id,
            )
        )

        confidence, breakdown = (
            calculate_confidence(
                dna=dna,
                preferences=preferences,
                quiz_answer_count=(
                    bundle.quiz_answer_count
                ),
                behavior_event_count=(
                    behavior_event_count
                ),
            )
        )

        evidence = {
            "quiz_answers": (
                bundle.quiz_answer_count
            ),
            "behavior_events": (
                behavior_event_count
            ),
        }

        version = (
            self.repository.next_profile_version(
                user_id,
            )
        )

        profile = (
            self.repository.create_style_profile(
                user_id=user_id,
                version=version,
                dna=dna,
                identity=identity,
                confidence=confidence,
                confidence_breakdown=breakdown,
                evidence=evidence,
            )
        )

        self.db.commit()
        self.db.refresh(profile)

        return {
            "profile_id": profile.profile_id,
            "version": profile.version,
            "dna": profile.dna_vector,
            "identity": profile.identity,
            "confidence": (
                profile.profile_confidence
            ),
            "confidence_breakdown": (
                profile.confidence_breakdown
            ),
            "evidence": profile.evidence,
        }

    def evolve_dna_from_event(
        self,
        *,
        user_id: int,
        event_type: str,
        item_vector: dict[str, float]
    ) -> None:
        """
        Evolve the user's Fashion DNA based on an item interaction event.
        Persists a new version of the StyleProfile if the DNA changes.
        """
        weights = {
            "view": 0.0,
            "save": 0.02,
            "wishlist": 0.03,
            "cart_add": 0.04,
            "purchase": 0.08,
            "keep": 0.12,
            "wear": 0.15,
            "return": -0.08,
            "recommendation_reject": -0.15,
        }
        alpha = weights.get(event_type, 0.0)
        if alpha == 0.0 or not item_vector:
            return

        from models import StyleProfile
        current_profile = self.db.query(StyleProfile).filter(
            StyleProfile.user_id == user_id
        ).order_by(StyleProfile.version.desc()).first()
        if not current_profile:
            return
            
        old_dna = current_profile.dna_vector
        new_scores = {}
        
        # Combine keys from both dicts
        all_keys = set(old_dna.keys()).union(item_vector.keys())
        
        for key in all_keys:
            old_val = old_dna.get(key, 0.0)
            item_val = item_vector.get(key, 0.0)
            
            if alpha > 0:
                # Positive influence: shift towards item vector
                new_val = old_val * (1 - alpha) + item_val * alpha
            else:
                # Negative influence: shift away from item vector
                abs_alpha = abs(alpha)
                # Penalise only if the item strongly features this trait
                penalty = item_val * abs_alpha
                new_val = max(0.0, old_val - penalty)
                
            new_scores[key] = new_val

        # Normalize back to 100%
        try:
            new_dna = normalize_dna(new_scores)
        except ValueError:
            return  # Can't normalize if all traits dropped to zero
            
        identity = build_identity(new_dna)
        
        behavior_event_count = self.repository.count_behavior_events(user_id)
        # Fetch preferences manually or assume preferences haven't changed
        user = self.repository.get_user(user_id)
        preferences = user.preferences if user else None
        
        confidence, breakdown = calculate_confidence(
            dna=new_dna,
            preferences=preferences,
            quiz_answer_count=current_profile.evidence.get("quiz_answers", 0),
            behavior_event_count=behavior_event_count,
        )
        
        evidence = current_profile.evidence.copy()
        evidence["behavior_events"] = behavior_event_count
        
        version = self.repository.next_profile_version(user_id)
        
        new_profile = self.repository.create_style_profile(
            user_id=user_id,
            version=version,
            dna=new_dna,
            identity=identity,
            confidence=confidence,
            confidence_breakdown=breakdown,
            evidence=evidence,
        )
        
        # Inherit the source attribute but note it was an event update
        new_profile.source = f"event_evolution_{event_type}"
        self.db.add(new_profile)
        self.db.commit()

    def blend_with_creator(
        self,
        user_dna: dict[str, float],
        creator_dna: dict[str, float],
        blend_pct: int,
    ) -> dict[str, int]:
        """Blend a percentage of the creator's DNA into the user's DNA."""
        user_weight = (100 - blend_pct) / 100.0
        creator_weight = blend_pct / 100.0
        merged_dna = {}

        for key in set(user_dna).union(creator_dna):
            merged_value = (user_dna.get(key, 0) * user_weight) + (
                creator_dna.get(key, 0) * creator_weight
            )
            if merged_value > 5:
                merged_dna[key] = int(round(merged_value))

        total = sum(merged_dna.values())
        if total > 0:
            merged_dna = {
                key: int(round((value / total) * 100))
                for key, value in merged_dna.items()
            }

        return merged_dna