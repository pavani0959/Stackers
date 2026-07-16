from __future__ import annotations

import re
from typing import Any

import models


def _humanise(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return text.replace("_", " ").replace("-", " ").strip().title()


class ExplanationGenerator:
    def generate(
        self,
        *,
        product: models.Product,
        overall_score: int,
        score_breakdown: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        if overall_score >= 85:
            summary = "This is a strong match for your current Fashion DNA."
        elif overall_score >= 70:
            summary = "This is a moderate match for your current profile."
        elif overall_score >= 55:
            summary = "This has a limited match with some supporting evidence."
        else:
            summary = "The available evidence shows a weak match."

        reasons = [
            self._style_reason(score_breakdown["style"]),
            self._occasion_reason(score_breakdown["occasion"]),
            self._budget_reason(product, score_breakdown["budget"]),
            self._wardrobe_reason(score_breakdown["wardrobe"]),
            self._season_reason(score_breakdown["season"]),
        ]

        limitations = [
            "Community purchase behaviour was not used because no verified aggregate source is available."
        ]

        wardrobe_evidence = score_breakdown["wardrobe"]["evidence"]
        if wardrobe_evidence.get("wardrobe_item_count", 0) == 0:
            limitations.append(
                "Wardrobe compatibility is neutral because no active wardrobe evidence is available."
            )

        budget_evidence = score_breakdown["budget"]["evidence"]
        if (
            budget_evidence.get("budget_min") is None
            and budget_evidence.get("budget_max") is None
            and not budget_evidence.get("budget_tier")
        ):
            limitations.append(
                "Budget compatibility is neutral because no saved budget evidence is available."
            )

        season_evidence = score_breakdown["season"]["evidence"]
        if not season_evidence.get("requested_season"):
            limitations.append(
                "Season compatibility does not use live weather; no season was supplied in the request context."
            )

        return {
            "summary": summary,
            "reasons": reasons,
            "limitations": limitations,
        }

    def _style_reason(self, component: dict[str, Any]) -> dict[str, Any]:
        evidence = component["evidence"]
        matches = evidence.get("matched_styles", [])
        primary = _humanise(evidence.get("primary_identity"))
        if matches:
            detail = (
                "The product shares the following saved style signals: "
                + ", ".join(_humanise(value) for value in matches)
                + "."
            )
        else:
            detail = (
                "No direct overlap was found between the product tags and "
                "your strongest saved Fashion DNA labels."
            )
        return {
            "code": "style_match",
            "title": f"Alignment with your {primary or 'Fashion DNA'}",
            "detail": detail,
            "score": component["score"],
            "evidence_source": component["evidence_source"],
        }

    def _occasion_reason(self, component: dict[str, Any]) -> dict[str, Any]:
        evidence = component["evidence"]
        requested = evidence.get("requested_occasion")
        matched = evidence.get("matched_occasions", [])
        if requested and component["score"] == 100:
            detail = (
                f"{_humanise(requested)} appears in the product's stored "
                "occasion tags."
            )
        elif matched:
            detail = (
                "The product overlaps with your saved occasion preferences: "
                + ", ".join(_humanise(value) for value in matched)
                + "."
            )
        elif requested:
            detail = (
                f"{_humanise(requested)} does not appear in the product's "
                "stored occasion tags."
            )
        else:
            detail = (
                "No matching saved occasion preference was found for this product."
            )
        return {
            "code": "occasion_match",
            "title": "Occasion compatibility",
            "detail": detail,
            "score": component["score"],
            "evidence_source": component["evidence_source"],
        }

    def _budget_reason(
        self,
        product: models.Product,
        component: dict[str, Any],
    ) -> dict[str, Any]:
        evidence = component["evidence"]
        budget_min = evidence.get("budget_min")
        budget_max = evidence.get("budget_max")
        over_by = evidence.get("over_budget_by")

        if over_by is not None and budget_max is not None:
            detail = (
                f"The ₹{product.price:,.0f} price is ₹{over_by:,.0f} above "
                f"your saved maximum of ₹{budget_max:,.0f}."
            )
        elif budget_min is not None and budget_max is not None:
            detail = (
                f"The ₹{product.price:,.0f} price is evaluated against your "
                f"saved ₹{budget_min:,.0f}–₹{budget_max:,.0f} range."
            )
        elif evidence.get("budget_tier"):
            detail = (
                "The product budget tier was compared with your saved budget tier."
            )
        else:
            detail = (
                "No numeric budget range is available, so this component uses a neutral score."
            )

        return {
            "code": "budget_match",
            "title": "Budget compatibility",
            "detail": detail,
            "score": component["score"],
            "evidence_source": component["evidence_source"],
        }

    def _wardrobe_reason(self, component: dict[str, Any]) -> dict[str, Any]:
        evidence = component["evidence"]
        count = evidence.get("wardrobe_item_count", 0)
        duplicates = evidence.get("duplicate_count", 0)
        complementary = evidence.get("complementary_count", 0)

        if count == 0:
            detail = (
                "No active wardrobe items are available, so the wardrobe score is neutral."
            )
        elif duplicates:
            detail = (
                f"{duplicates} same-colour, same-subcategory wardrobe item(s) "
                "reduced this score."
            )
        elif complementary:
            detail = (
                f"{complementary} active wardrobe item(s) are in complementary categories."
            )
        else:
            detail = (
                "Active wardrobe evidence exists, but no duplicate or complementary category signal was found."
            )

        return {
            "code": "wardrobe_match",
            "title": "Wardrobe compatibility",
            "detail": detail,
            "score": component["score"],
            "evidence_source": component["evidence_source"],
        }

    def _season_reason(self, component: dict[str, Any]) -> dict[str, Any]:
        evidence = component["evidence"]
        requested = evidence.get("requested_season")
        product_season = evidence.get("product_season")
        if requested:
            detail = (
                f"The requested {_humanise(requested)} context was compared "
                f"with the product's {_humanise(product_season)} season tag."
            )
        else:
            detail = (
                f"The product is tagged for {_humanise(product_season)}; no "
                "live weather or requested season was used."
            )

        return {
            "code": "season_match",
            "title": "Season compatibility",
            "detail": detail,
            "score": component["score"],
            "evidence_source": component["evidence_source"],
        }
