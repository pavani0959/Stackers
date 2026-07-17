from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from typing import Any

from repositories.style_twin_repository import (
    StyleTwinRecord,
    StyleTwinRepository,
)


DNA_WEIGHT = 0.60
BUDGET_WEIGHT = 0.15
OCCASION_WEIGHT = 0.15
COLOUR_WEIGHT = 0.10

MINIMUM_SIMILARITY = 70.0

MAX_PRODUCT_INSIGHTS = 5

BUDGET_TIER_RANGES = {
    "budget-explorer": (
        0.0,
        500.0,
    ),
    "campus-casual": (
        0.0,
        1000.0,
    ),
    "smart-spender": (
        500.0,
        1500.0,
    ),
    "mid-range": (
        1000.0,
        3000.0,
    ),
    "premium": (
        2500.0,
        10000.0,
    ),
}


def _normalize_token(
    value: object,
) -> str:
    return "".join(
        character
        for character in str(value).lower()
        if character.isalnum()
    )


def _display_trait(
    value: str,
) -> str:
    expanded = re.sub(
        r"([a-z])([A-Z])",
        r"\1 \2",
        value,
    )

    return (
        expanded
        .replace("_", " ")
        .replace("-", " ")
        .strip()
        .lower()
    )


def _number(
    value: object,
) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return None


def _to_string_set(
    value: Any,
) -> set[str]:
    if value is None:
        return set()

    parsed_value = value

    if isinstance(value, str):
        stripped = value.strip()

        if not stripped:
            return set()

        try:
            parsed_value = json.loads(
                stripped,
            )
        except (
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ):
            parsed_value = [
                item.strip()
                for item in stripped.split(",")
            ]

    if isinstance(
        parsed_value,
        dict,
    ):
        iterable = parsed_value.keys()
    elif isinstance(
        parsed_value,
        (
            list,
            tuple,
            set,
        ),
    ):
        iterable = parsed_value
    else:
        iterable = [
            parsed_value,
        ]

    return {
        _normalize_token(item)
        for item in iterable
        if str(item).strip()
    }


def _dna_map(
    value: Any,
) -> dict[str, float]:
    if not isinstance(
        value,
        dict,
    ):
        return {}

    result: dict[str, float] = {}

    for key, raw_score in value.items():
        score = _number(
            raw_score,
        )

        if score is None:
            continue

        normalized_key = _normalize_token(
            key,
        )

        if not normalized_key:
            continue

        result[normalized_key] = max(
            0.0,
            score,
        )

    return result


def dna_similarity(
    first_dna: Any,
    second_dna: Any,
) -> float:
    first = _dna_map(
        first_dna,
    )

    second = _dna_map(
        second_dna,
    )

    keys = sorted(
        set(first)
        | set(second),
    )

    if not keys:
        return 0.0

    dot_product = sum(
        first.get(key, 0.0)
        * second.get(key, 0.0)
        for key in keys
    )

    first_norm = math.sqrt(
        sum(
            first.get(key, 0.0) ** 2
            for key in keys
        ),
    )

    second_norm = math.sqrt(
        sum(
            second.get(key, 0.0) ** 2
            for key in keys
        ),
    )

    if (
        first_norm == 0
        or second_norm == 0
    ):
        return 0.0

    return round(
        dot_product
        / (
            first_norm
            * second_norm
        )
        * 100,
        2,
    )


def _budget_range(
    preference: object | None,
) -> tuple[float, float] | None:
    if preference is None:
        return None

    minimum = _number(
        getattr(
            preference,
            "budget_min",
            None,
        ),
    )

    maximum = _number(
        getattr(
            preference,
            "budget_max",
            None,
        ),
    )

    if (
        minimum is not None
        and maximum is not None
    ):
        low = min(
            minimum,
            maximum,
        )

        high = max(
            minimum,
            maximum,
        )

        return (
            low,
            high,
        )

    tier = str(
        getattr(
            preference,
            "budget_tier",
            "",
        )
        or ""
    ).strip().lower()

    return BUDGET_TIER_RANGES.get(
        tier,
    )


def budget_similarity(
    first_preference: object | None,
    second_preference: object | None,
) -> float:
    first_range = _budget_range(
        first_preference,
    )

    second_range = _budget_range(
        second_preference,
    )

    if (
        first_range is None
        or second_range is None
    ):
        first_tier = str(
            getattr(
                first_preference,
                "budget_tier",
                "",
            )
            or ""
        ).strip().lower()

        second_tier = str(
            getattr(
                second_preference,
                "budget_tier",
                "",
            )
            or ""
        ).strip().lower()

        if (
            first_tier
            and first_tier == second_tier
        ):
            return 100.0

        return 0.0

    first_min, first_max = (
        first_range
    )

    second_min, second_max = (
        second_range
    )

    overlap = max(
        0.0,
        min(
            first_max,
            second_max,
        )
        - max(
            first_min,
            second_min,
        ),
    )

    union = (
        max(
            first_max,
            second_max,
        )
        - min(
            first_min,
            second_min,
        )
    )

    if union == 0:
        return 100.0

    return round(
        overlap
        / union
        * 100,
        2,
    )


def overlap_similarity(
    first_value: Any,
    second_value: Any,
) -> float:
    first = _to_string_set(
        first_value,
    )

    second = _to_string_set(
        second_value,
    )

    if (
        not first
        or not second
    ):
        return 0.0

    union = first | second

    if not union:
        return 0.0

    return round(
        len(first & second)
        / len(union)
        * 100,
        2,
    )


def _event_type_value(
    event_type: object,
) -> str:
    value = getattr(
        event_type,
        "value",
        event_type,
    )

    return str(
        value,
    ).strip().lower()


def _shared_traits(
    current_profile: object,
    candidate: StyleTwinRecord,
    current_preference: object | None,
) -> list[str]:
    current_dna = _dna_map(
        getattr(
            current_profile,
            "dna_vector",
            {},
        ),
    )

    candidate_dna = _dna_map(
        getattr(
            candidate.profile,
            "dna_vector",
            {},
        ),
    )

    shared_dna = sorted(
        set(current_dna)
        & set(candidate_dna),
        key=lambda key: (
            -min(
                current_dna[key],
                candidate_dna[key],
            ),
            key,
        ),
    )

    traits = [
        _display_trait(key)
        for key in shared_dna
        if (
            current_dna[key] >= 10
            and candidate_dna[key] >= 10
        )
    ]

    preference_fields = (
        "preferred_aesthetics",
        "preferred_occasions",
        "preferred_colours",
    )

    for field_name in preference_fields:
        current_values = _to_string_set(
            getattr(
                current_preference,
                field_name,
                None,
            ),
        )

        candidate_values = _to_string_set(
            getattr(
                candidate.preference,
                field_name,
                None,
            ),
        )

        for token in sorted(
            current_values
            & candidate_values,
        ):
            display_value = _display_trait(
                token,
            )

            if display_value not in traits:
                traits.append(
                    display_value,
                )

    return traits[:5]


class StyleTwinService:
    def __init__(
        self,
        repository: StyleTwinRepository,
    ) -> None:
        self.repository = repository

    def _product_insights(
        self,
        cohort_user_ids: list[int],
    ) -> list[dict[str, object]]:
        events = (
            self.repository
            .get_cohort_events(
                cohort_user_ids,
            )
        )

        counts: dict[
            int,
            dict[str, int],
        ] = {}

        for event in events:
            if event.product_id is None:
                continue

            product_counts = (
                counts.setdefault(
                    event.product_id,
                    {
                        "keep_count": 0,
                        "return_count": 0,
                    },
                )
            )

            event_type = _event_type_value(
                event.event_type,
            )

            if event_type in {
                "keep",
                "wear",
            }:
                product_counts[
                    "keep_count"
                ] += 1

            elif event_type == "return":
                product_counts[
                    "return_count"
                ] += 1

        insights = []

        for (
            product_id,
            product_counts,
        ) in counts.items():
            keep_count = product_counts[
                "keep_count"
            ]

            return_count = product_counts[
                "return_count"
            ]

            denominator = (
                keep_count
                + return_count
            )

            keep_rate = (
                round(
                    keep_count
                    / denominator
                    * 100,
                    2,
                )
                if denominator
                else None
            )

            insights.append({
                "product_id": product_id,
                "keep_count": keep_count,
                "return_count": return_count,
                "keep_rate": keep_rate,
            })

        insights.sort(
            key=lambda insight: (
                -(
                    insight["keep_count"]
                    + insight[
                        "return_count"
                    ]
                ),
                -(
                    insight["keep_rate"]
                    if (
                        insight[
                            "keep_rate"
                        ]
                        is not None
                    )
                    else -1
                ),
                insight["product_id"],
            ),
        )

        return insights[
            :MAX_PRODUCT_INSIGHTS
        ]

    def find_twins(
        self,
        current_user_id: int,
    ) -> dict[str, object]:
        current_profile = (
            self.repository
            .get_latest_profile(
                current_user_id,
            )
        )

        if current_profile is None:
            raise ValueError(
                "Complete your Fashion DNA "
                "before finding Style Twins."
            )

        current_preference = (
            self.repository
            .get_preference(
                current_user_id,
            )
        )

        candidates = (
            self.repository
            .get_candidate_records(
                current_user_id,
            )
        )

        scored_candidates = []

        for candidate in candidates:
            dna_score = dna_similarity(
                current_profile.dna_vector,
                candidate.profile.dna_vector,
            )

            budget_score = (
                budget_similarity(
                    current_preference,
                    candidate.preference,
                )
            )

            occasion_score = (
                overlap_similarity(
                    getattr(
                        current_preference,
                        "preferred_occasions",
                        None,
                    ),
                    getattr(
                        candidate.preference,
                        "preferred_occasions",
                        None,
                    ),
                )
            )

            colour_score = (
                overlap_similarity(
                    getattr(
                        current_preference,
                        "preferred_colours",
                        None,
                    ),
                    getattr(
                        candidate.preference,
                        "preferred_colours",
                        None,
                    ),
                )
            )

            similarity = round(
                dna_score
                * DNA_WEIGHT
                + budget_score
                * BUDGET_WEIGHT
                + occasion_score
                * OCCASION_WEIGHT
                + colour_score
                * COLOUR_WEIGHT,
                2,
            )

            if (
                similarity
                < MINIMUM_SIMILARITY
            ):
                continue

            scored_candidates.append({
                "record": candidate,
                "similarity": similarity,
                "shared_traits": (
                    _shared_traits(
                        current_profile,
                        candidate,
                        current_preference,
                    )
                ),
            })

        scored_candidates.sort(
            key=lambda item: (
                -item["similarity"],
                item["record"].user.id,
            ),
        )

        cohort_user_ids = [
            item["record"].user.id
            for item in scored_candidates
        ]

        cohort_size = len(
            cohort_user_ids,
        )

        product_insights = (
            self._product_insights(
                cohort_user_ids,
            )
        )

        twins = [
            {
                "user_id": (
                    item["record"].user.id
                ),
                "name": (
                    item["record"].user.name
                ),
                "similarity": (
                    item["similarity"]
                ),
                "cohort_size": cohort_size,
                "shared_traits": (
                    item["shared_traits"]
                ),
                "product_insights": (
                    product_insights
                ),
            }
            for item in scored_candidates
        ]

        return {
            "dataset": {
                "type": "seeded_demo",
                "label": (
                    "Insights use a seeded "
                    "demo cohort"
                ),
                "generated_at": datetime.now(
                    timezone.utc,
                ),
            },
            "threshold": (
                MINIMUM_SIMILARITY
            ),
            "twins": twins,
        }

    def list_static_profiles(
        self,
    ) -> list[dict[str, object]]:
        rows = (
            self.repository
            .get_static_community_profiles()
        )

        result = []

        for row in rows:
            raw_dna = getattr(
                row,
                "dna_json",
                None,
            )

            if isinstance(
                raw_dna,
                dict,
            ):
                dna = raw_dna

            else:
                try:
                    dna = json.loads(
                        raw_dna or "{}",
                    )
                except (
                    TypeError,
                    ValueError,
                    json.JSONDecodeError,
                ):
                    dna = {}

            result.append({
                "id": row.id,
                "name": row.name,
                "handle": row.handle,
                "avatar": row.avatar,
                "role": row.role or "",
                "dna": {
                    str(key): float(value)
                    for key, value
                    in dna.items()
                },
                "dna_label": (
                    row.dna_label
                ),
                "recent_purchases": (
                    row.recent_purchases
                ),
            })

        return result
