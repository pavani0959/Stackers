"""outfit_builder.py — Phase 5 Reverse Shopping outfit assembly.

This module takes the structured intent from intent_parser and a ranked
list of scored products, then generates up to three diverse, budget-safe
complete outfits with a real score breakdown for each.
"""
from __future__ import annotations

import uuid
from itertools import product as cartesian_product
from typing import Any


# ---------------------------------------------------------------------------
# Score helpers
# ---------------------------------------------------------------------------

def _safe_base_score(item: dict) -> float:
    """Return a 0-100 numeric confidence from whatever shape the item carries."""
    conf = item.get("confidence", item.get("match", 80))
    if isinstance(conf, dict):
        return float(conf.get("overall", 80))
    try:
        return float(conf)
    except (TypeError, ValueError):
        return 80.0


def _style_score(items: tuple[dict, ...], occasion: str | None) -> int:
    """How well do the items' tags match the target occasion?"""
    if not occasion:
        return 75
    occ_norm = occasion.lower().replace("_", " ")
    hits = sum(
        1
        for item in items
        for tag in (item.get("tags") or [])
        if occ_norm in tag.lower() or tag.lower() in occ_norm
    )
    return min(100, 60 + hits * 10)


def _coherence_score(items: tuple[dict, ...]) -> int:
    """Shared tags across items indicate visual/aesthetic coherence."""
    tag_sets = [set(item.get("tags") or []) for item in items]
    if len(tag_sets) < 2:
        return 75
    pairs = 0
    for i in range(len(tag_sets)):
        for j in range(i + 1, len(tag_sets)):
            pairs += len(tag_sets[i].intersection(tag_sets[j]))
    return min(100, 50 + pairs * 15)


def _budget_score(total: int, budget_limit: int) -> int:
    """How well does the total price fit the budget?"""
    if budget_limit <= 0:
        return 80
    if total <= budget_limit:
        # Penalise outfits that leave too much budget unused (undershoot by >40%)
        leftover_pct = (budget_limit - total) / budget_limit
        return max(70, round(100 - leftover_pct * 25))
    # Over budget (should not happen after hard filter, but guard anyway)
    over_pct = (total - budget_limit) / budget_limit
    return max(0, round(60 - over_pct * 100))


def _category_completeness(items: tuple[dict, ...]) -> int:
    """Reward outfits that cover core category roles: top+bottom+footwear."""
    cats = {item.get("category", "").lower() for item in items}
    score = 70
    if "top" in cats or "dress" in cats:
        score += 10
    if "bottom" in cats or "dress" in cats:
        score += 10
    if "footwear" in cats:
        score += 10
    return min(100, score)


def _combination_score(
    items: tuple[dict, ...],
    budget_limit: int,
    occasion: str | None,
) -> tuple[int, dict[str, int]]:
    """Return (overall_score_0_100, breakdown_dict)."""
    base = round(sum(_safe_base_score(i) for i in items) / len(items))
    total = sum(item["price"] for item in items)

    breakdown = {
        "style":    _style_score(items, occasion),
        "occasion": _style_score(items, occasion),   # same signal for now
        "budget":   _budget_score(total, budget_limit),
        "weather":  80,                               # no live weather; neutral
        "wardrobe": _coherence_score(items),
    }

    # Weighted per audit spec: style 30%, occasion 25%, budget 15%, weather 10%, wardrobe 15% + 5% base
    overall = (
        breakdown["style"]    * 0.30
        + breakdown["occasion"] * 0.25
        + breakdown["budget"]   * 0.15
        + breakdown["weather"]  * 0.10
        + breakdown["wardrobe"] * 0.15
        + base                  * 0.05
    )
    return int(round(min(100, max(0, overall)))), breakdown


# ---------------------------------------------------------------------------
# Diversity selection
# ---------------------------------------------------------------------------

def _select_diverse(
    candidates: list[dict],
    maximum: int = 3,
) -> list[dict]:
    """
    Select deterministic, distinct outfits.

    Fully disjoint outfits are preferred. When
    three fully disjoint outfits are unavailable,
    limited product reuse is permitted, but each
    complete item combination must still be unique.
    """
    selected: list[dict] = []

    seen_combinations: set[
        frozenset[int]
    ] = set()

    used_ids: set[int] = set()

    # First pass: select completely disjoint
    # outfits wherever possible.
    for candidate in candidates:
        combination = frozenset(
            item["id"]
            for item in candidate["items"]
        )

        if combination in seen_combinations:
            continue

        if not combination.isdisjoint(
            used_ids
        ):
            continue

        selected.append(candidate)

        seen_combinations.add(
            combination
        )

        used_ids.update(
            combination
        )

        if len(selected) == maximum:
            return selected

    # Second pass: permit the smallest possible
    # overlap, but never duplicate the complete
    # outfit combination.
    remaining = []

    for candidate in candidates:
        combination = frozenset(
            item["id"]
            for item in candidate["items"]
        )

        if combination in seen_combinations:
            continue

        overlap_count = len(
            combination.intersection(
                used_ids
            )
        )

        remaining.append(
            (
                overlap_count,
                candidate,
                combination,
            )
        )

    remaining.sort(
        key=lambda entry: (
            entry[0],
            -entry[1]["overall_score"],
            entry[1]["total_price"],
            tuple(
                item["id"]
                for item
                in entry[1]["items"]
            ),
        ),
    )

    for (
        _overlap_count,
        candidate,
        combination,
    ) in remaining:
        if combination in seen_combinations:
            continue

        selected.append(candidate)

        seen_combinations.add(
            combination
        )

        used_ids.update(
            combination
        )

        if len(selected) == maximum:
            break

    return selected

def _why_lines(
    label: str,
    total: int,
    budget_limit: int,
    occasion: str | None,
    breakdown: dict[str, int],
) -> list[str]:
    lines: list[str] = []
    if occasion:
        lines.append(f"Built for a {occasion.replace('_', ' ')} occasion.")
    lines.append(f"₹{total:,} — within your ₹{budget_limit:,} budget.")
    if breakdown["wardrobe"] >= 80:
        lines.append("Strong aesthetic coherence across all pieces.")
    if label == "Budget Smart":
        saved = budget_limit - total
        lines.append(f"₹{saved:,} saved — most budget-efficient option.")
    if label == "Style Stretch":
        lines.append("Pushes the style boundary while respecting your budget.")
    return lines


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_outfits(
    intent: dict,
    scored_products: list[dict],
    fallback_budget: int,
) -> dict[str, Any]:
    """
    Generate up to three diverse, budget-safe outfits.

    Returns a dict with keys:
      session_id    — ephemeral UUID for this generation call
      parsed_intent — the structured intent dict
      outfits       — list of outfit dicts (0-3 items)
      error         — only present when no outfit could be built
    """
    budget_limit: int = intent.get("budget_total") or fallback_budget
    occasion: str | None = intent.get("occasion")

    tops = _candidate_pool([
        product
        for product in scored_products
        if product.get("category")
        == "top"
    ])

    bottoms = _candidate_pool([
        product
        for product in scored_products
        if product.get("category")
        == "bottom"
    ])

    footwear = _candidate_pool([
        product
        for product in scored_products
        if product.get("category")
        == "footwear"
    ])

    accessories = _candidate_pool([
        product
        for product in scored_products
        if product.get("category")
        == "accessory"
    ])

    # Prefer footwear as third slot; fall back to accessories
    third_pool = footwear if footwear else accessories

    if not tops or not bottoms or not third_pool:
        missing = []
        if not tops:       missing.append("tops")
        if not bottoms:    missing.append("bottoms")
        if not third_pool: missing.append("footwear/accessories")
        return {
            "session_id": str(uuid.uuid4()),
            "parsed_intent": intent,
            "outfits": [],
            "error": (
                f"Not enough catalogue items to build a complete outfit "
                f"(missing: {', '.join(missing)})."
            ),
        }

    candidates: list[dict] = []

    for top, bottom, third in cartesian_product(
        tops,
        bottoms,
        third_pool,
    ):
        items = (
            top,
            bottom,
            third,
        )

        item_ids = [
            item["id"]
            for item in items
        ]

        # Never allow the same product twice
        # inside one complete outfit.
        if (
            len(item_ids)
            != len(set(item_ids))
        ):
            continue

        total = sum(
            int(item["price"])
            for item in items
        )

        # The prompt budget is a hard limit.
        if total > budget_limit:
            continue

        overall, breakdown = (
            _combination_score(
                items,
                budget_limit,
                occasion,
            )
        )
        candidates.append({
            "id":            str(uuid.uuid4()),
            "items":         list(items),
            "total_price":   total,
            "overall_score": overall,
            "breakdown":     breakdown,
        })

    if not candidates:
        return {
            "session_id": str(uuid.uuid4()),
            "parsed_intent": intent,
            "outfits": [],
            "error": (
                f"No complete 3-item outfit fits within ₹{budget_limit:,}. "
                "Try increasing the budget or broadening the occasion."
            ),
        }

    candidates.sort(
        key=lambda outfit: (
            -outfit["overall_score"],
            outfit["total_price"],
            tuple(
                item["id"]
                for item
                in outfit["items"]
            ),
        ),
    )
    selected = _select_diverse(candidates, maximum=3)

    labels = ["Best Match", "Budget Smart", "Style Stretch"]
    for idx, outfit in enumerate(selected):
        label = labels[idx] if idx < len(labels) else f"Outfit {idx + 1}"
        outfit["label"] = label
        outfit["why"] = _why_lines(
            label,
            outfit["total_price"],
            budget_limit,
            occasion,
            outfit["breakdown"],
        )

    return {
        "session_id": str(uuid.uuid4()),
        "parsed_intent": intent,
        "outfits": selected,
    }

def _candidate_pool(
    products: list[dict],
    *,
    maximum: int = 24,
) -> list[dict]:
    ranked = sorted(
        products,
        key=lambda item: (
            -item.get("final_score", 0),
            item["price"],
            item["id"],
        ),
    )

    affordable = sorted(
        products,
        key=lambda item: (
            item["price"],
            -item.get("final_score", 0),
            item["id"],
        ),
    )

    selected: list[dict] = []
    seen: set[int] = set()

    for item in ranked[:16] + affordable[:12]:
        item_id = item["id"]

        if item_id in seen:
            continue

        selected.append(item)
        seen.add(item_id)

        if len(selected) >= maximum:
            break

    return selected
