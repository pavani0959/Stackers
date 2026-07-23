from __future__ import annotations

import re
from typing import Any

import models

DECISION_MODEL_VERSION = "decision-v1.0.0"

COMPONENT_WEIGHTS = {
    "style": 0.30,
    "occasion": 0.20,
    "budget": 0.15,
    "wardrobe": 0.15,
    "season": 0.10,
    "vibe": 0.10,
}

_CATEGORY_ALIASES = {
    "tops": "top",
    "tshirt": "top",
    "tshirts": "top",
    "shirt": "top",
    "shirts": "top",
    "bottoms": "bottom",
    "trouser": "bottom",
    "trousers": "bottom",
    "pants": "bottom",
    "jeans": "bottom",
    "shoes": "footwear",
    "shoe": "footwear",
    "accessories": "accessory",
    "bags": "accessory",
}

_COMPLEMENTARY_CATEGORIES = {
    "top": {"bottom", "footwear", "outerwear", "accessory"},
    "bottom": {"top", "footwear", "outerwear", "accessory"},
    "dress": {"footwear", "outerwear", "accessory"},
    "footwear": {"top", "bottom", "dress", "outerwear"},
    "outerwear": {"top", "bottom", "dress", "footwear"},
    "accessory": {"top", "bottom", "dress", "outerwear"},
}


def clamp_score(value: float) -> int:
    return max(0, min(100, round(value)))


def _normalise_token(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _normalise_list(values: Any) -> list[str]:
    if not values:
        return []
    if isinstance(values, list):
        return [str(value) for value in values if value is not None]
    return [str(values)]


def _category(value: Any) -> str:
    normalised = _normalise_token(value)
    return _CATEGORY_ALIASES.get(normalised, normalised)


def _component(
    *,
    score: int,
    weight: float,
    evidence_source: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "score": score,
        "weight": weight,
        "weighted_score": round(score * weight, 2),
        "evidence_source": evidence_source,
        "evidence": evidence,
    }


class DecisionScoreCalculator:
    def calculate(
        self,
        *,
        style_profile: models.StyleProfile,
        preferences: models.UserPreference | None,
        product: models.Product,
        wardrobe_items: list[models.WardrobeItem],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        components = {
            "style": self._style_component(
                style_profile=style_profile,
                preferences=preferences,
                product=product,
            ),
            "occasion": self._occasion_component(
                preferences=preferences,
                product=product,
                context=context,
            ),
            "budget": self._budget_component(
                preferences=preferences,
                product=product,
            ),
            "wardrobe": self._wardrobe_component(
                wardrobe_items=wardrobe_items,
                product=product,
            ),
            "season": self._season_component(
                product=product,
                context=context,
            ),
            "vibe": self._vibe_component(
                product=product,
                context=context,
            ),
        }

        overall_score = clamp_score(
            sum(
                component["weighted_score"]
                for component in components.values()
            )
        )

        return {
            "overall_score": overall_score,
            "score_breakdown": components,
        }

    def _style_component(
        self,
        *,
        style_profile: models.StyleProfile,
        preferences: models.UserPreference | None,
        product: models.Product,
    ) -> dict[str, Any]:
        dna = {
            str(label): float(value)
            for label, value in (style_profile.dna_vector or {}).items()
            if float(value) > 0
        }
        product_tags = _normalise_list(product.tags)
        product_tokens = {
            _normalise_token(value)
            for value in [
                *product_tags,
                product.category,
                product.subcategory,
            ]
            if value
        }

        matched_styles = [
            label
            for label in dna
            if _normalise_token(label) in product_tokens
        ]
        matched_dna_weight = sum(dna[label] for label in matched_styles)

        preferred_aesthetics = _normalise_list(
            preferences.preferred_aesthetics if preferences else []
        )
        matched_preferences = [
            aesthetic
            for aesthetic in preferred_aesthetics
            if _normalise_token(aesthetic) in product_tokens
        ]

        primary_identity = style_profile.primary_identity or ""
        primary_identity_match = (
            _normalise_token(primary_identity) in product_tokens
        )

        score = clamp_score(
            40
            + (matched_dna_weight * 0.50)
            + min(len(matched_preferences) * 5, 10)
            + (5 if primary_identity_match else 0)
        )

        return _component(
            score=score,
            weight=COMPONENT_WEIGHTS["style"],
            evidence_source="style_profile",
            evidence={
                "profile_version": style_profile.version,
                "primary_identity": primary_identity,
                "matched_styles": matched_styles,
                "matched_dna_weight": round(matched_dna_weight, 2),
                "product_tags": product_tags,
                "preferred_aesthetics": preferred_aesthetics,
                "matched_preferred_aesthetics": matched_preferences,
            },
        )

    def _occasion_component(
        self,
        *,
        preferences: models.UserPreference | None,
        product: models.Product,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        product_occasions = _normalise_list(product.occasions)
        product_lookup = {
            _normalise_token(value): value
            for value in product_occasions
        }

        requested_occasion = context.get("occasion")
        requested_key = _normalise_token(requested_occasion)

        preferred_occasions = _normalise_list(
            preferences.preferred_occasions if preferences else []
        )
        preferred_lookup = {
            _normalise_token(value): value
            for value in preferred_occasions
        }
        overlaps = sorted(
            set(product_lookup).intersection(preferred_lookup)
        )

        raw_priorities = (
            preferences.occasion_priorities
            if preferences and preferences.occasion_priorities
            else {}
        )
        priorities = {
            _normalise_token(key): max(0.0, min(1.0, float(value)))
            for key, value in raw_priorities.items()
        }

        if requested_key:
            if requested_key in product_lookup:
                score = 100
            elif overlaps:
                highest_priority = max(
                    (priorities.get(key, 0.5) for key in overlaps),
                    default=0.5,
                )
                score = clamp_score(65 + (30 * highest_priority))
            else:
                score = 30
        elif overlaps:
            highest_priority = max(
                (priorities.get(key, 0.5) for key in overlaps),
                default=0.5,
            )
            score = clamp_score(65 + (30 * highest_priority))
        elif not preferred_occasions:
            score = 60
        else:
            score = 30

        return _component(
            score=score,
            weight=COMPONENT_WEIGHTS["occasion"],
            evidence_source=(
                "request_context"
                if requested_key
                else "user_preferences"
            ),
            evidence={
                "requested_occasion": requested_occasion,
                "product_occasions": product_occasions,
                "preferred_occasions": preferred_occasions,
                "matched_occasions": [
                    product_lookup[key]
                    for key in overlaps
                ],
                "occasion_priorities": raw_priorities,
            },
        )

    def _budget_component(
        self,
        *,
        preferences: models.UserPreference | None,
        product: models.Product,
    ) -> dict[str, Any]:
        budget_min = preferences.budget_min if preferences else None
        budget_max = preferences.budget_max if preferences else None
        budget_tier = preferences.budget_tier if preferences else None
        product_price = float(product.price)
        over_budget_by = None

        if budget_min is not None or budget_max is not None:
            if budget_max is not None and product_price > budget_max:
                over_budget_by = round(product_price - budget_max, 2)
                if budget_max <= 0:
                    score = 0
                else:
                    ratio = over_budget_by / budget_max
                    if ratio <= 0.10:
                        score = clamp_score(90 - (ratio * 150))
                    elif ratio <= 0.50:
                        score = clamp_score(
                            75 - (((ratio - 0.10) / 0.40) * 55)
                        )
                    else:
                        score = clamp_score(
                            20 - (((ratio - 0.50) / 0.50) * 20)
                        )
            elif budget_min is not None and product_price < budget_min:
                score = 90
            else:
                score = 100
        elif budget_tier:
            score = (
                85
                if _normalise_token(product.budgetTier)
                == _normalise_token(budget_tier)
                else 60
            )
        else:
            score = 60

        return _component(
            score=score,
            weight=COMPONENT_WEIGHTS["budget"],
            evidence_source="user_preferences",
            evidence={
                "budget_min": budget_min,
                "budget_max": budget_max,
                "budget_tier": budget_tier,
                "product_budget_tier": product.budgetTier,
                "product_price": product_price,
                "over_budget_by": over_budget_by,
            },
        )

    def _wardrobe_component(
        self,
        *,
        wardrobe_items: list[models.WardrobeItem],
        product: models.Product,
    ) -> dict[str, Any]:
        active_items = [
            item
            for item in wardrobe_items
            if getattr(item, "is_active", True)
        ]

        product_category = _category(product.category)
        product_subcategory = _normalise_token(product.subcategory)
        product_colour = _normalise_token(product.primary_colour)
        product_tags = {
            _normalise_token(tag)
            for tag in _normalise_list(product.tags)
        }

        duplicate_items = []
        complementary_items = []
        matching_tag_count = 0

        for item in active_items:
            item_category = _category(item.category)
            item_subcategory = _normalise_token(item.subcategory)
            item_colour = _normalise_token(item.primary_colour)

            if (
                product_subcategory
                and product_colour
                and item_subcategory == product_subcategory
                and item_colour == product_colour
            ):
                duplicate_items.append(item)

            if item_category in _COMPLEMENTARY_CATEGORIES.get(
                product_category,
                set(),
            ):
                complementary_items.append(item)

            item_tags = {
                _normalise_token(tag)
                for tag in _normalise_list(item.tags)
            }
            matching_tag_count += len(product_tags.intersection(item_tags))

        if not active_items:
            score = 60
        else:
            score = clamp_score(
                60
                + min(len(complementary_items) * 6, 24)
                + min(matching_tag_count * 3, 12)
                - min(len(duplicate_items) * 18, 36)
            )

        return _component(
            score=score,
            weight=COMPONENT_WEIGHTS["wardrobe"],
            evidence_source="wardrobe_items",
            evidence={
                "wardrobe_item_count": len(active_items),
                "complementary_count": len(complementary_items),
                "complementary_categories": sorted(
                    {
                        item.category
                        for item in complementary_items
                    }
                ),
                "duplicate_count": len(duplicate_items),
                "duplicate_item_ids": [item.id for item in duplicate_items],
                "subcategory": product.subcategory,
                "primary_colour": product.primary_colour,
                "matching_tag_count": matching_tag_count,
            },
        )

    def _season_component(
        self,
        *,
        product: models.Product,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        requested_season = context.get("season")
        requested_key = _normalise_token(requested_season)
        product_season = product.season
        product_key = _normalise_token(product_season)

        if product_key in {"allseason", "allyear", "yearround"}:
            score = 100
        elif not requested_key:
            score = 70
        elif product_key == requested_key:
            score = 95
        else:
            score = 45

        return _component(
            score=score,
            weight=COMPONENT_WEIGHTS["season"],
            evidence_source="request_context",
            evidence={
                "requested_season": requested_season,
                "product_season": product_season,
            },
        )

    def _vibe_component(
        self,
        *,
        product: models.Product,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        requested_vibe = context.get("vibe")
        vibe_key = _normalise_token(requested_vibe)
        
        product_tags = {
            _normalise_token(tag)
            for tag in _normalise_list(product.tags)
        }
        product_occasions = {
            _normalise_token(occ)
            for occ in _normalise_list(product.occasions)
        }
        
        vibe_mappings = {
            "quiet": {"minimalist", "neutral", "quietluxury", "classic", "elegant"},
            "bold": {"bold", "colorful", "streetwear", "y2k", "statement"},
            "grind": {"office", "comfort", "smartcasual", "formal", "casual", "everyday"},
            "night": {"party", "evening", "date", "wedding"},
        }
        
        score = 50
        matched_tags = []
        if vibe_key and vibe_key in vibe_mappings:
            target_tags = vibe_mappings[vibe_key]
            matched = target_tags.intersection(product_tags.union(product_occasions))
            matched_tags = list(matched)
            if matched_tags:
                score = clamp_score(50 + (len(matched_tags) * 25))
            else:
                score = 30
                
        return _component(
            score=score,
            weight=COMPONENT_WEIGHTS["vibe"],
            evidence_source="request_context" if vibe_key else "default",
            evidence={
                "requested_vibe": requested_vibe,
                "matched_vibe_tags": matched_tags,
            },
        )
