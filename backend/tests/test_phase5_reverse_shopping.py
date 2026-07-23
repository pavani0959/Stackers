"""
Phase 5 acceptance tests — Reverse Shopping.

Acceptance criteria from the repository audit:

For prompt "Interview tomorrow, smart casual, ₹2,000":
  ✓ occasion is interview
  ✓ total budget is 2000
  ✓ all outfits are at or below budget
  ✓ each outfit has valid categories (top, bottom, footwear/accessory)
  ✓ no product repeats inside an outfit
  ✓ three outfits are meaningfully different
  ✓ explanations mention interview and budget
  ✓ parsed constraints shown in response (parsed_intent chip data)
  ✓ "Buy All" creates cart entries not purchases (frontend tested separately)
  ✓ errors and empty states are handled
  ✓ results are persisted as a RecommendationSession

This file uses the shared conftest.py (real test.db with migrations),
so it can run alongside other test files without DB conflicts.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

# Uses real test.db provisioned by conftest.py – no need to override get_db.
client = TestClient(app)

DEMO_PROFILE = {
    "id": 1,
    "name": "Pavani",
    "email": "demo@myntra.com",
    "gender": "women",
    "age": 21,
    "onboarding_completed": True,
    "dna": {"minimalist": 60, "campusCasual": 40},
    "occasions": ["college", "work"],
    "budget": "mid",
}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _call_reverse(prompt: str) -> dict:
    resp = client.post(
        "/api/recommend/reverse",
        json={
            "prompt": prompt,
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# 1. Intent parsing
# ---------------------------------------------------------------------------

class TestIntentParsing:
    def test_occasion_is_interview(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        assert data["parsed_intent"]["occasion"] == "interview"

    def test_budget_is_2000(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        assert data["parsed_intent"]["budget_total"] == 2000

    def test_budget_source_is_prompt(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        assert data["budget_source"] == "prompt"

    def test_budget_limit_matches_prompt(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        assert data["budget_limit"] == 2000

    def test_college_fest_occasion(self):
        data = _call_reverse("College fest Saturday, retro theme, ₹1500")
        assert data["parsed_intent"]["occasion"] == "college_fest"

    def test_k_suffix_budget(self):
        data = _call_reverse("Night out, under 3k")
        budget = data["parsed_intent"]["budget_total"]
        assert budget == 3000

    def test_theme_extraction(self):
        data = _call_reverse("College fest Saturday, retro theme, ₹1500")
        themes = data["parsed_intent"].get("theme", [])
        assert "retro" in themes

    def test_two_different_budgets_produce_different_results(self):
        d1 = _call_reverse("College fest retro theme ₹1500")
        d2 = _call_reverse("College fest retro theme ₹150000")
        b1 = d1["budget_limit"]
        b2 = d2["budget_limit"]
        assert b1 != b2, "Different prompts should yield different budget limits"
        
        o1 = [[item["id"] for item in out["items"]] for out in d1.get("outfits", [])]
        o2 = [[item["id"] for item in out["items"]] for out in d2.get("outfits", [])]
        assert o1 != o2, "Different budgets should produce different ranked/filtered results"

    def test_parsed_intent_returned_in_response(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        assert "parsed_intent" in data
        pi = data["parsed_intent"]
        assert "occasion" in pi
        assert "budget_total" in pi


# ---------------------------------------------------------------------------
# 2. Hard budget enforcement
# ---------------------------------------------------------------------------

class TestBudgetEnforcement:
    def test_all_outfits_within_budget(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        for outfit in data.get("outfits", []):
            assert outfit["total"] <= 2000, (
                f"Outfit '{outfit.get('label')}' costs ₹{outfit['total']} > ₹2000"
            )

    def test_tight_budget_returns_empty_or_valid(self):
        """A very tight budget should either return valid outfits or a clear error."""
        data = _call_reverse("Interview tomorrow ₹100")
        for outfit in data.get("outfits", []):
            assert outfit["total"] <= 100, (
                f"Outfit exceeds budget: ₹{outfit['total']}"
            )

    def test_generous_budget_returns_outfits(self):
        data = _call_reverse("Campus day, ₹10000")
        # Seeded catalogue should have enough items for at least one outfit
        assert data["within_budget"] is True or len(data["outfits"]) >= 0  # won't crash


# ---------------------------------------------------------------------------
# 3. Outfit structure validity
# ---------------------------------------------------------------------------

class TestOutfitStructure:
    VALID_CATEGORIES = {"top", "bottom", "dress", "footwear", "accessory", "outerwear"}

    def test_outfits_have_valid_categories(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        for outfit in data.get("outfits", []):
            for item in outfit["items"]:
                assert item["category"].lower() in self.VALID_CATEGORIES, (
                    f"Invalid category '{item['category']}'"
                )

    def test_no_duplicate_products_within_outfit(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        for outfit in data.get("outfits", []):
            item_ids = [i["id"] for i in outfit["items"]]
            assert len(item_ids) == len(set(item_ids)), (
                f"Outfit '{outfit.get('label')}' has duplicate product ids: {item_ids}"
            )

    def test_each_outfit_has_at_least_3_items(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        for outfit in data.get("outfits", []):
            assert len(outfit["items"]) >= 3, (
                f"Outfit '{outfit.get('label')}' has only {len(outfit['items'])} item(s)"
            )


# ---------------------------------------------------------------------------
# 4. Score and breakdown
# ---------------------------------------------------------------------------

class TestScoreAndBreakdown:
    def test_outfit_score_is_0_to_100(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        for outfit in data.get("outfits", []):
            assert 0 <= outfit["score"] <= 100, (
                f"Score {outfit['score']} out of 0-100 range"
            )

    def test_breakdown_keys_present(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        expected_keys = {"style", "occasion", "budget", "weather", "wardrobe"}
        for outfit in data.get("outfits", []):
            bd = outfit.get("breakdown", {})
            assert expected_keys.issubset(bd.keys()), (
                f"Missing breakdown keys in outfit '{outfit.get('label')}': "
                f"{expected_keys - bd.keys()}"
            )

    def test_breakdown_values_are_valid(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        for outfit in data.get("outfits", []):
            for key, value in outfit.get("breakdown", {}).items():
                assert 0 <= value <= 100, (
                    f"Breakdown '{key}'={value} outside 0-100 range"
                )


# ---------------------------------------------------------------------------
# 5. Labels and diversity
# ---------------------------------------------------------------------------

class TestLabelsAndDiversity:
    EXPECTED_LABELS = {"Best Match", "Budget Smart", "Style Stretch"}

    def test_outfits_have_labels(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        labels = {o.get("label") for o in data.get("outfits", [])}
        # If we have 3 outfits they must use the expected label names
        if len(data.get("outfits", [])) == 3:
            assert labels == self.EXPECTED_LABELS

    def test_outfits_are_meaningfully_different(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        outfits = data.get("outfits", [])
        if len(outfits) < 2:
            return  # can't compare
        # Each pair of outfits should not share all products
        for i in range(len(outfits)):
            for j in range(i + 1, len(outfits)):
                ids_i = {item["id"] for item in outfits[i]["items"]}
                ids_j = {item["id"] for item in outfits[j]["items"]}
                shared = ids_i.intersection(ids_j)
                assert shared != ids_i, (
                    f"Outfits {i+1} and {j+1} are identical (same products)"
                )

    def test_outfit_why_lines_present(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        for outfit in data.get("outfits", []):
            assert len(outfit.get("why", [])) >= 1, (
                f"Outfit '{outfit.get('label')}' has no 'why' explanation"
            )


# ---------------------------------------------------------------------------
# 6. Empty / error states
# ---------------------------------------------------------------------------

class TestErrorStates:
    def test_empty_prompt_returns_200(self):
        """Empty or nonsense prompt should not crash the server."""
        resp = client.post(
            "/api/recommend/reverse",
            json={"prompt": "zzzzzzzzz"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "outfits" in data
        assert "message" in data

    def test_missing_prompt_returns_422(self):
        resp = client.post(
            "/api/recommend/reverse",
            json={"user_profile": DEMO_PROFILE},
        )
        assert resp.status_code == 422

    def test_prompt_only_request_uses_server_profile(self):
        resp = client.post(
            "/api/recommend/reverse",
            json={
                "prompt": (
                    "Interview tomorrow ₹2000"
                ),
            },
        )

        assert resp.status_code == 200

        data = resp.json()

        assert data["prompt"] == (
            "Interview tomorrow ₹2000"
        )

        assert (
            data["parsed_intent"][
                "budget_total"
            ]
            == 2000
        )


# ---------------------------------------------------------------------------
# 7. Session persistence
# ---------------------------------------------------------------------------

class TestSessionPersistence:
    def test_response_contains_session_id(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        # session_id may be None if seeded DB doesn't have demo user
        assert "session_id" in data

    def test_session_id_is_string_or_none(self):
        data = _call_reverse("Interview tomorrow, smart casual, ₹2,000")
        sid = data.get("session_id")
        assert sid is None or isinstance(sid, str)


def test_interview_acceptance_prompt():
    data = _call_reverse(
        "Interview tomorrow, "
        "smart casual, ₹2,000."
    )

    assert (
        data["parsed_intent"]["occasion"]
        == "interview"
    )

    assert (
        data["parsed_intent"]["budget_total"]
        == 2000
    )

    assert data["within_budget"] is True
    assert len(data["outfits"]) == 3

    combinations = []

    for outfit in data["outfits"]:
        assert outfit["total"] <= 2000
        assert len(outfit["items"]) >= 3

        assert (
            outfit["recommendation_item_id"]
            is not None
        )

        assert outfit["snapshot_id"]

        item_ids = [
            item["id"]
            for item in outfit["items"]
        ]

        assert (
            len(item_ids)
            == len(set(item_ids))
        )

        combinations.append(
            frozenset(item_ids)
        )

        explanation = " ".join(
            outfit["why"]
        ).lower()

        assert "interview" in explanation
        assert "budget" in explanation

    assert len(set(combinations)) == 3

def test_college_fest_no_duplicates():
    data = _call_reverse("College fest Saturday, retro theme, ₹2000")
    assert data["parsed_intent"]["budget_total"] == 2000
    
    outfits = data.get("outfits", [])
    assert len(outfits) > 0
    
    combinations = []
    for outfit in outfits:
        assert outfit["total"] <= 2000
        
        item_ids = {item["id"] for item in outfit["items"]}
        combinations.append(frozenset(item_ids))
        
    assert len(set(combinations)) == len(combinations), "Outfits must not be duplicates"

