from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from config import get_settings
from database import SessionLocal
from main import app
from models import StyleProfile


client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_demo_user_style_profile():
    """
    The Phase 7 endpoint correctly requires a
    persisted Fashion DNA profile.

    The isolated pytest database does not always
    include one for the configured demo user, so
    this fixture creates one for each test only
    when it is missing.
    """
    settings = get_settings()
    user_id = settings.demo_user_id

    db = SessionLocal()
    created_profile_id = None

    try:
        existing_profile = (
            db.query(StyleProfile)
            .filter(
                StyleProfile.user_id
                == user_id
            )
            .order_by(
                StyleProfile.version.desc(),
                StyleProfile.id.desc(),
            )
            .first()
        )

        if existing_profile is None:
            profile = StyleProfile(
                user_id=user_id,
                profile_id=uuid4(),
                version=1,
                dna_vector={
                    "minimalist": 70.0,
                    "streetwear": 30.0,
                },
                primary_identity=(
                    "Minimalist"
                ),
                secondary_identity=(
                    "Streetwear"
                ),
                profile_confidence=85,
                source="pytest",
                model_version=(
                    "phase7-style-twin-test"
                ),
                identity={
                    "name": "Minimalist",
                    "description": (
                        "Phase 7 isolated "
                        "test profile."
                    ),
                },
                confidence_breakdown={
                    "quiz_completeness": 40,
                    "answer_consistency": 25,
                    "preference_coverage": 20,
                    "behavior_evidence": 0,
                },
                evidence={
                    "source": "pytest",
                    "purpose": (
                        "style_twin_endpoint_test"
                    ),
                },
            )

            db.add(profile)
            db.commit()
            db.refresh(profile)

            created_profile_id = profile.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    yield

    if created_profile_id is None:
        return

    cleanup_db = SessionLocal()

    try:
        (
            cleanup_db.query(StyleProfile)
            .filter(
                StyleProfile.id
                == created_profile_id
            )
            .delete(
                synchronize_session=False,
            )
        )

        cleanup_db.commit()

    except Exception:
        cleanup_db.rollback()
        raise

    finally:
        cleanup_db.close()


def _get_twins() -> dict:
    response = client.get(
        "/api/community/twins",
    )

    assert (
        response.status_code == 200
    ), response.text

    return response.json()


def test_twins_endpoint_is_get_only():
    paths = app.openapi()["paths"]

    twin_methods = paths[
        "/api/community/twins"
    ]

    assert "get" in twin_methods
    assert "post" not in twin_methods


def test_current_user_is_not_returned_as_own_twin():
    data = _get_twins()

    current_user_id = (
        get_settings().demo_user_id
    )

    returned_user_ids = {
        twin["user_id"]
        for twin in data["twins"]
    }

    assert (
        current_user_id
        not in returned_user_ids
    )


def test_every_twin_meets_minimum_similarity():
    data = _get_twins()

    assert data["threshold"] == 70.0

    for twin in data["twins"]:
        assert (
            twin["similarity"]
            >= data["threshold"]
        )


def test_similarity_results_are_deterministic():
    first = _get_twins()
    second = _get_twins()

    assert first["threshold"] == (
        second["threshold"]
    )

    assert first["twins"] == (
        second["twins"]
    )


def test_dataset_is_disclosed_as_seeded_demo():
    data = _get_twins()

    assert (
        data["dataset"]["type"]
        == "seeded_demo"
    )

    assert (
        data["dataset"]["label"]
        == (
            "Insights use a seeded "
            "demo cohort"
        )
    )

    assert (
        data["dataset"]["generated_at"]
    )


def test_keep_rates_always_have_denominators():
    data = _get_twins()

    for twin in data["twins"]:
        for insight in (
            twin["product_insights"]
        ):
            keep_count = (
                insight["keep_count"]
            )

            return_count = (
                insight["return_count"]
            )

            denominator = (
                keep_count
                + return_count
            )

            assert denominator > 0

            expected = round(
                keep_count
                / denominator
                * 100,
                2,
            )

            assert (
                insight["keep_rate"]
                == expected
            )


def test_creators_are_separate_from_twins():
    paths = app.openapi()["paths"]

    assert (
        "/api/community/profiles"
        in paths
    )

    data = _get_twins()

    for twin in data["twins"]:
        assert "role" not in twin
        assert "dna" not in twin
        assert "creator" not in {
            str(trait).lower()
            for trait
            in twin["shared_traits"]
        }


def test_frontend_uses_get_without_user_profile():
    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    source = (
        project_root
        / "src"
        / "screens"
        / "Community"
        / "Community.jsx"
    ).read_text(
        encoding="utf-8",
    )

    assert re.search(
        (
            r"apiRequest\(\s*"
            r"['\"]"
            r"/api/community/twins"
            r"['\"]\s*\)"
        ),
        source,
    )

    old_request = re.search(
        (
            r"/api/community/twins"
            r"[\s\S]{0,220}"
            r"user_profile"
        ),
        source,
    )

    assert old_request is None

    assert (
        "normalizedRole === 'creator'"
        in source
    )

    assert (
        "normalizedRole === 'community'"
        in source
    )

    assert (
        "Users with a >90% match"
        not in source
    )

    assert (
        "Recently bought X items"
        not in source
    )
