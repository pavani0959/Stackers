from __future__ import annotations

from typing import Any

import models


class RegretSignalService:
    def generate(
        self,
        *,
        product: models.Product,
        preferences: models.UserPreference | None,
        score_breakdown: dict[str, dict[str, Any]],
        category_return_count: int,
    ) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []

        budget_max = preferences.budget_max if preferences else None
        if budget_max is not None and product.price > budget_max:
            over_by = round(float(product.price) - budget_max, 2)
            signals.append(
                {
                    "code": "over_budget",
                    "severity": (
                        "high"
                        if budget_max > 0 and over_by / budget_max > 0.20
                        else "medium"
                    ),
                    "title": "Above your saved budget",
                    "detail": (
                        f"This item is ₹{over_by:,.0f} above your "
                        f"saved maximum of ₹{budget_max:,.0f}."
                    ),
                    "evidence": {
                        "budget_max": budget_max,
                        "product_price": float(product.price),
                        "over_budget_by": over_by,
                    },
                }
            )

        style_score = score_breakdown["style"]["score"]
        if style_score < 55:
            signals.append(
                {
                    "code": "weak_style_alignment",
                    "severity": "medium",
                    "title": "Limited Fashion DNA alignment",
                    "detail": (
                        "The product has limited overlap with your current "
                        "saved Fashion DNA and aesthetic preferences."
                    ),
                    "evidence": {
                        "style_score": style_score,
                        "matched_styles": score_breakdown["style"][
                            "evidence"
                        ].get("matched_styles", []),
                    },
                }
            )

        occasion_score = score_breakdown["occasion"]["score"]
        if occasion_score < 50:
            signals.append(
                {
                    "code": "occasion_mismatch",
                    "severity": "medium",
                    "title": "Weak occasion fit",
                    "detail": (
                        "The selected occasion does not match the product's "
                        "stored occasion tags."
                    ),
                    "evidence": {
                        "occasion_score": occasion_score,
                        **score_breakdown["occasion"]["evidence"],
                    },
                }
            )

        wardrobe_evidence = score_breakdown["wardrobe"]["evidence"]
        duplicate_count = int(wardrobe_evidence.get("duplicate_count", 0))
        if duplicate_count > 0:
            signals.append(
                {
                    "code": "wardrobe_duplicate",
                    "severity": "medium",
                    "title": "Similar item already in your wardrobe",
                    "detail": (
                        f"Your wardrobe contains {duplicate_count} active "
                        "item(s) with the same subcategory and colour."
                    ),
                    "evidence": {
                        "duplicate_count": duplicate_count,
                        "subcategory": wardrobe_evidence.get("subcategory"),
                        "primary_colour": wardrobe_evidence.get(
                            "primary_colour"
                        ),
                        "duplicate_item_ids": wardrobe_evidence.get(
                            "duplicate_item_ids",
                            [],
                        ),
                    },
                }
            )

        if category_return_count > 0:
            signals.append(
                {
                    "code": "category_return_history",
                    "severity": "low",
                    "title": "Previous return in this category",
                    "detail": (
                        f"Your recorded history contains "
                        f"{category_return_count} return event(s) for this "
                        "product category."
                    ),
                    "evidence": {
                        "category": product.category,
                        "return_count": category_return_count,
                    },
                }
            )

        return signals
