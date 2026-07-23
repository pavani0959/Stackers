from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

import models
import schemas


STYLE_KEYWORDS = {
    "minimalist": (
        "minimalist",
        "minimal",
        "clean",
        "neutral",
    ),
    "streetwear": (
        "streetwear",
        "street wear",
        "street",
        "oversized",
    ),
    "campusCasual": (
        "campus casual",
        "campus",
        "casual",
        "everyday",
    ),
    "quietLuxury": (
        "quiet luxury",
        "luxury",
        "premium",
        "tailored",
    ),
    "y2k": (
        "y2k",
        "2000s",
        "retro",
    ),
}


def _normalize_key(value: object) -> str:
    return "".join(
        character
        for character in str(value).lower()
        if character.isalnum()
    )


def _normalize_dna(
    dna: dict[str, float],
) -> dict[str, float]:
    positive = {
        key: max(
            0.0,
            float(value),
        )
        for key, value in dna.items()
        if float(value) > 0
    }

    total = sum(
        positive.values(),
    )

    if total <= 0:
        return {
            "exploration": 100.0,
        }

    normalized = {
        key: round(
            value * 100.0 / total,
            2,
        )
        for key, value in positive.items()
    }

    difference = round(
        100.0
        - sum(normalized.values()),
        2,
    )

    if normalized and difference:
        largest_key = max(
            normalized,
            key=normalized.get,
        )

        normalized[largest_key] = round(
            normalized[largest_key]
            + difference,
            2,
        )

    return normalized


def _build_return_dna(
    current_dna: dict[str, float],
    wardrobe_item: models.WardrobeItem,
) -> dict[str, float]:
    """
    Materially reduce the returned item's strongest
    matching style signal and redistribute that weight.

    The transformation is deterministic and keeps
    the vector normalized to 100.
    """
    updated_dna = {
        key: float(value)
        for key, value
        in dict(current_dna or {}).items()
    }

    if not updated_dna:
        return {
            "exploration": 100.0,
        }

    tags = (
        wardrobe_item.tags
        if isinstance(
            wardrobe_item.tags,
            list,
        )
        else []
    )

    searchable_text = " ".join(
        str(value)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        for value in [
            wardrobe_item.name,
            wardrobe_item.category,
            wardrobe_item.subcategory,
            *tags,
        ]
        if value
    )

    normalized_keyword_map = {
        _normalize_key(style_key): keywords
        for style_key, keywords
        in STYLE_KEYWORDS.items()
    }

    matched_keys = []

    for dna_key in updated_dna:
        normalized_dna_key = _normalize_key(
            dna_key,
        )

        keywords = (
            normalized_keyword_map.get(
                normalized_dna_key,
                (),
            )
        )

        direct_key_match = (
            normalized_dna_key
            and normalized_dna_key
            in _normalize_key(
                searchable_text,
            )
        )

        keyword_match = any(
            keyword in searchable_text
            for keyword in keywords
        )

        if (
            direct_key_match
            or keyword_match
        ):
            matched_keys.append(
                dna_key,
            )

    if matched_keys:
        target_key = max(
            matched_keys,
            key=lambda key: (
                updated_dna[key],
                key,
            ),
        )
    else:
        target_key = max(
            updated_dna,
            key=lambda key: (
                updated_dna[key],
                key,
            ),
        )

    recipient_candidates = [
        key
        for key in updated_dna
        if key != target_key
    ]

    if recipient_candidates:
        recipient_key = min(
            recipient_candidates,
            key=lambda key: (
                updated_dna[key],
                key,
            ),
        )
    else:
        recipient_key = "exploration"
        updated_dna[recipient_key] = 0.0

    target_value = updated_dna[
        target_key
    ]

    transfer = min(
        6.0,
        max(
            2.0,
            target_value * 0.08,
        ),
    )

    transfer = min(
        transfer,
        max(
            0.0,
            target_value - 0.01,
        ),
    )

    updated_dna[target_key] = (
        target_value
        - transfer
    )

    updated_dna[recipient_key] = (
        updated_dna.get(
            recipient_key,
            0.0,
        )
        + transfer
    )

    return _normalize_dna(
        updated_dna,
    )


class MemoryService:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def checkout(
        self,
        *,
        user_id: int,
        payload: schemas.CheckoutRequest,
    ) -> schemas.CheckoutResponse:
        purchase_event_ids: list[int] = []
        wardrobe_item_ids: list[int] = []

        for checkout_item in payload.items:
            product = (
                self.db.query(
                    models.Product,
                )
                .filter(
                    models.Product.id
                    == checkout_item.product_id,
                    models.Product.is_active.is_(
                        True,
                    ),
                )
                .one_or_none()
            )

            if product is None:
                raise ValueError(
                    "One or more products "
                    "are unavailable."
                )

            purchased_at = datetime.now(
                timezone.utc,
            )

            wardrobe_item = (
                models.WardrobeItem(
                    user_id=user_id,
                    product_id=product.id,
                    source="purchase",
                    name=product.name,
                    category=product.category,
                    subcategory=(
                        product.subcategory
                    ),
                    primary_colour=(
                        product.primary_colour
                    ),
                    size=checkout_item.size,
                    image_url=product.image,
                    tags=list(
                        product.tags or [],
                    ),
                    purchase_price=(
                        product.price
                    ),
                    purchase_date=(
                        purchased_at
                    ),
                    is_active=True,
                )
            )

            self.db.add(
                wardrobe_item,
            )

            self.db.flush()

            purchase_event = (
                models.UserEvent(
                    user_id=user_id,
                    product_id=product.id,
                    wardrobe_item_id=(
                        wardrobe_item.id
                    ),
                    recommendation_item_id=(
                        checkout_item
                        .recommendation_item_id
                    ),
                    event_type="purchase",
                    event_metadata={
                        "source": "checkout",
                        "size": (
                            checkout_item.size
                        ),
                        "decision_snapshot_id": (
                            str(
                                checkout_item
                                .decision_snapshot_id
                            )
                            if (
                                checkout_item
                                .decision_snapshot_id
                            )
                            else None
                        ),
                        "price_at_purchase": (
                            product.price
                        ),
                    },
                    occurred_at=purchased_at,
                )
            )

            self.db.add(
                purchase_event,
            )

            self.db.flush()

            purchase_event_ids.append(
                purchase_event.id,
            )

            wardrobe_item_ids.append(
                wardrobe_item.id,
            )

        return schemas.CheckoutResponse(
            purchase_event_ids=(
                purchase_event_ids
            ),
            wardrobe_item_ids=(
                wardrobe_item_ids
            ),
        )

    def _create_return_profile(
        self,
        *,
        user_id: int,
        wardrobe_item: models.WardrobeItem,
        event_reason: str | None,
    ) -> models.StyleProfile | None:
        latest_profile = (
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

        if latest_profile is None:
            return None

        previous_dna = dict(
            latest_profile.dna_vector
            or {},
        )

        evolved_dna = _build_return_dna(
            previous_dna,
            wardrobe_item,
        )

        if evolved_dna == previous_dna:
            raise ValueError(
                "Return did not produce a "
                "material DNA change."
            )

        ranked_traits = sorted(
            evolved_dna.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        )

        primary_identity = (
            ranked_traits[0][0]
            if ranked_traits
            else latest_profile
            .primary_identity
        )

        secondary_identity = (
            ranked_traits[1][0]
            if len(ranked_traits) > 1
            else None
        )

        evidence = deepcopy(
            latest_profile.evidence
            or {},
        )

        evidence.update({
            "latest_behavior": {
                "event_type": "return",
                "wardrobe_item_id": (
                    wardrobe_item.id
                ),
                "product_id": (
                    wardrobe_item.product_id
                ),
                "reason": event_reason,
            },
            "previous_profile_id": str(
                latest_profile.profile_id,
            ),
            "previous_version": (
                latest_profile.version
            ),
        })

        identity = deepcopy(
            latest_profile.identity
            or {},
        )

        identity.update({
            "primary": primary_identity,
            "secondary": secondary_identity,
        })

        candidate_values = {
            "user_id": user_id,
            "profile_id": uuid4(),
            "version": (
                latest_profile.version
                + 1
            ),
            "dna_vector": evolved_dna,
            "primary_identity": (
                primary_identity
            ),
            "secondary_identity": (
                secondary_identity
            ),
            "profile_confidence": (
                latest_profile
                .profile_confidence
            ),
            "source": "behavior_return",
            "model_version": (
                "dna-behavior-v1.0.0"
            ),
            "identity": identity,
            "confidence_breakdown": (
                deepcopy(
                    latest_profile
                    .confidence_breakdown
                    or {},
                )
            ),
            "evidence": evidence,
        }

        model_columns = {
            column.name
            for column
            in models.StyleProfile
            .__table__.columns
        }

        ignored_columns = {
            "id",
            "created_at",
            "updated_at",
            "seed_key",
        }

        # Copy any additional model fields that
        # exist in this project and are not already
        # explicitly updated above.
        for column_name in model_columns:
            if (
                column_name in ignored_columns
                or column_name
                in candidate_values
            ):
                continue

            previous_value = getattr(
                latest_profile,
                column_name,
                None,
            )

            if previous_value is not None:
                candidate_values[
                    column_name
                ] = deepcopy(
                    previous_value,
                )

        profile_values = {
            key: value
            for key, value
            in candidate_values.items()
            if key in model_columns
        }

        evolved_profile = (
            models.StyleProfile(
                **profile_values,
            )
        )

        self.db.add(
            evolved_profile,
        )

        self.db.flush()

        return evolved_profile

    def record_action(
        self,
        *,
        user_id: int,
        wardrobe_item_id: int,
        event_type: str,
        reason: str | None,
    ) -> schemas.MemoryActionResponse:
        if event_type not in {
            "keep",
            "return",
        }:
            raise ValueError(
                "Unsupported memory action: "
                f"{event_type}"
            )

        wardrobe_item = (
            self.db.query(
                models.WardrobeItem,
            )
            .filter(
                models.WardrobeItem.id
                == wardrobe_item_id,
                models.WardrobeItem.user_id
                == user_id,
            )
            .one_or_none()
        )

        if wardrobe_item is None:
            raise LookupError(
                "Wardrobe item was not found."
            )

        if (
            event_type == "return"
            and not wardrobe_item.is_active
        ):
            raise ValueError(
                "This wardrobe item has "
                "already been returned."
            )

        occurred_at = datetime.now(
            timezone.utc,
        )

        evolved_profile = None

        if event_type == "return":
            wardrobe_item.is_active = False

            evolved_profile = (
                self._create_return_profile(
                    user_id=user_id,
                    wardrobe_item=(
                        wardrobe_item
                    ),
                    event_reason=reason,
                )
            )

        action_event = models.UserEvent(
            user_id=user_id,
            product_id=(
                wardrobe_item.product_id
            ),
            wardrobe_item_id=(
                wardrobe_item.id
            ),
            event_type=event_type,
            event_metadata={
                "source": "fashion_memory",
                "reason": reason,
                "decision_changed": (
                    event_type == "return"
                ),
                "dna_profile_version": (
                    evolved_profile.version
                    if evolved_profile
                    else None
                ),
                "dna_profile_id": (
                    str(
                        evolved_profile
                        .profile_id
                    )
                    if evolved_profile
                    else None
                ),
            },
            occurred_at=occurred_at,
        )

        self.db.add(
            action_event,
        )

        self.db.flush()

        return schemas.MemoryActionResponse(
            event_id=action_event.id,
            wardrobe_item_id=(
                wardrobe_item.id
            ),
            event_type=event_type,
        )
