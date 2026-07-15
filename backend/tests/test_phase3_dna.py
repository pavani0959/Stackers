import os
from copy import deepcopy
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


os.environ.setdefault(
    "DATABASE_URL",
    "sqlite+pysqlite:///:memory:",
)
os.environ.setdefault(
    "ENVIRONMENT",
    "test",
)
os.environ.setdefault(
    "DEMO_USER_ID",
    "1",
)
os.environ.setdefault(
    "FRONTEND_ORIGINS",
    '["http://127.0.0.1:5173"]',
)


import models  # noqa: E402
from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402
from repositories.profile_repository import (  # noqa: E402
    ProfileRepository,
)
from services.dna_service import (  # noqa: E402
    build_identity,
    normalize_dna,
)


TEST_DATABASE_URL = (
    "sqlite+pysqlite:///:memory:"
)

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


VALID_ANSWERS = [
    {
        "question_id": "everyday-look",
        "choice_id": "minimal-campus",
    },
    {
        "question_id": "silhouette",
        "choice_id": "relaxed-fit",
    },
    {
        "question_id": "brand-personality",
        "choice_id": "clean-premium",
    },
    {
        "question_id": "colour-palette",
        "choice_id": "neutral-palette",
    },
    {
        "question_id": "comfort-expression",
        "choice_id": "comfort-balanced",
    },
    {
        "question_id": "occasion-priority",
        "choice_id": "campus-priority",
    },
    {
        "question_id": "shopping-motivation",
        "choice_id": "versatility-first",
    },
    {
        "question_id": "fashion-goal",
        "choice_id": "shop-smarter",
    },
]


@pytest.fixture()
def db_session():
    Base.metadata.drop_all(
        bind=test_engine,
    )
    Base.metadata.create_all(
        bind=test_engine,
    )

    session = TestingSessionLocal()

    user = models.User(
        id=1,
        seed_key="phase3-test-user",
        name="Test Style Explorer",
        email="phase3-test@example.com",
        gender="female",
        age=21,
        onboarding_completed=True,
        is_synthetic=True,
    )

    session.add(user)
    session.flush()

    preferences = models.UserPreference(
        user_id=user.id,
    )

    session.add(preferences)
    session.commit()

    try:
        yield session
    finally:
        session.close()

        Base.metadata.drop_all(
            bind=test_engine,
        )


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def post_dna(
    client: TestClient,
    answers: list[dict] | None = None,
):
    return client.post(
        "/api/profile/dna/calculate",
        json={
            "answers": (
                answers
                if answers is not None
                else deepcopy(VALID_ANSWERS)
            ),
        },
    )


def find_identity_update_route():
    schema = app.openapi()

    for path, methods in (
        schema["paths"].items()
    ):
        if (
            path.startswith(
                "/api/profile",
            )
            and "identity" in path
        ):
            for method in (
                "patch",
                "put",
            ):
                if method in methods:
                    return path, method

    raise AssertionError(
        "No profile identity update route "
        "was found. Expected a PATCH or PUT "
        "route containing '/identity'.",
    )


def test_dna_totals_exactly_100():
    dna = normalize_dna(
        {
            "minimalist": 7,
            "streetwear": 4,
            "quietLuxury": 3,
            "y2k": 2,
        },
    )

    assert round(
        sum(dna.values()),
        2,
    ) == 100


def test_dna_is_deterministic():
    scores = {
        "minimalist": 7,
        "streetwear": 4,
        "quietLuxury": 3,
        "y2k": 2,
    }

    first = normalize_dna(scores)
    second = normalize_dna(scores)

    assert first == second


def test_identity_is_deterministic():
    dna = normalize_dna(
        {
            "minimalist": 8,
            "quietLuxury": 6,
            "streetwear": 2,
        },
    )

    first = build_identity(dna)
    second = build_identity(dna)

    assert first == second


def test_normalize_dna_rejects_zero_total():
    with pytest.raises(
        ValueError,
        match="positive total",
    ):
        normalize_dna(
            {
                "minimalist": 0,
                "streetwear": 0,
            },
        )


def test_dna_requires_exactly_eight_answers(
    client,
):
    incomplete_answers = deepcopy(
        VALID_ANSWERS[:-1],
    )

    response = post_dna(
        client,
        incomplete_answers,
    )

    assert response.status_code == 422


def test_dna_rejects_unknown_question(
    client,
):
    answers = deepcopy(VALID_ANSWERS)

    answers[0]["question_id"] = (
        "unknown-question"
    )

    response = post_dna(
        client,
        answers,
    )

    assert response.status_code == 422


def test_dna_rejects_unknown_choice(
    client,
):
    answers = deepcopy(VALID_ANSWERS)

    answers[0]["choice_id"] = (
        "unknown-choice"
    )

    response = post_dna(
        client,
        answers,
    )

    assert response.status_code == 422


def test_response_contains_uuid_and_contract(
    client,
):
    response = post_dna(client)

    assert response.status_code == 200

    payload = response.json()

    UUID(
        str(
            payload["profile_id"],
        ),
    )

    assert payload["version"] == 1
    assert payload["dna"]
    assert payload["identity"]
    assert isinstance(
        payload["confidence"],
        int,
    )
    assert payload[
        "confidence_breakdown"
    ]
    assert payload["evidence"]


def test_api_dna_totals_exactly_100(
    client,
):
    response = post_dna(client)

    assert response.status_code == 200

    payload = response.json()

    assert round(
        sum(
            payload["dna"].values(),
        ),
        2,
    ) == 100


def test_profile_version_increments(
    client,
):
    first_response = post_dna(client)
    second_response = post_dna(client)

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_payload = first_response.json()
    second_payload = second_response.json()

    assert first_payload["version"] == 1
    assert second_payload["version"] == 2

    assert (
        first_payload["profile_id"]
        != second_payload["profile_id"]
    )


def test_confidence_breakdown_totals_to_confidence(
    client,
):
    response = post_dna(client)

    assert response.status_code == 200

    payload = response.json()

    breakdown_total = sum(
        payload[
            "confidence_breakdown"
        ].values(),
    )

    assert breakdown_total == payload[
        "confidence"
    ]

    assert (
        payload["confidence"]
        <= 100
    )

    assert (
        payload["confidence"]
        >= 0
    )


def test_identity_and_evidence_are_persisted(
    client,
    db_session,
):
    response = post_dna(client)

    assert response.status_code == 200

    payload = response.json()

    db_session.expire_all()

    saved_profile = (
        db_session.query(
            models.StyleProfile,
        )
        .filter(
            models.StyleProfile.profile_id
            == UUID(
                payload["profile_id"],
            ),
        )
        .first()
    )

    assert saved_profile is not None

    assert (
        saved_profile.identity
        == payload["identity"]
    )

    assert (
        saved_profile.evidence
        == payload["evidence"]
    )

    assert (
        saved_profile.confidence_breakdown
        == payload[
            "confidence_breakdown"
        ]
    )

    assert round(
        sum(
            saved_profile.dna_vector.values(),
        ),
        2,
    ) == 100


def test_behavior_event_count_appears_in_evidence(
    client,
    monkeypatch,
):
    def fake_behavior_count(
        self,
        user_id,
    ):
        assert user_id == 1
        return 7

    monkeypatch.setattr(
        ProfileRepository,
        "count_behavior_events",
        fake_behavior_count,
    )

    response = post_dna(client)

    assert response.status_code == 200

    payload = response.json()

    assert payload["evidence"][
        "behavior_events"
    ] == 7

    assert payload[
        "confidence_breakdown"
    ]["behavior_evidence"] > 0


def test_get_profile_returns_latest_profile(
    client,
):
    first_response = post_dna(client)
    second_response = post_dna(client)

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    latest_created = (
        second_response.json()
    )

    profile_response = client.get(
        "/api/profile",
    )

    assert profile_response.status_code == 200

    profile_payload = (
        profile_response.json()
    )

    style_profile = profile_payload[
        "style_profile"
    ]

    assert style_profile is not None

    assert (
        style_profile["profile_id"]
        == latest_created["profile_id"]
    )

    assert (
        style_profile["version"]
        == latest_created["version"]
    )

    assert (
        style_profile["identity"]
        == latest_created["identity"]
    )

    assert (
        style_profile[
            "confidence_breakdown"
        ]
        == latest_created[
            "confidence_breakdown"
        ]
    )

    assert (
        style_profile["evidence"]
        == latest_created["evidence"]
    )


def test_get_profile_contains_complete_preferences(
    client,
):
    response = post_dna(client)

    assert response.status_code == 200

    profile_response = client.get(
        "/api/profile",
    )

    assert profile_response.status_code == 200

    payload = profile_response.json()
    preferences = payload["preferences"]

    assert preferences is not None

    expected_fields = {
        "budget_min",
        "budget_max",
        "budget_tier",
        "preferred_occasions",
        "preferred_colours",
        "preferred_brands",
        "preferred_aesthetics",
        "fit_preferences",
        "comfort_priority",
        "trend_openness",
        "fashion_goal",
        "comfort_expression_balance",
        "occasion_priorities",
    }

    assert expected_fields.issubset(
        preferences.keys(),
    )


def test_identity_partial_update_preserves_unset_fields(
    client,
    db_session,
):
    user_before = (
        db_session.query(models.User)
        .filter(models.User.id == 1)
        .first()
    )

    assert user_before is not None

    original_gender = user_before.gender
    original_age = user_before.age

    original_onboarding_status = (
        user_before.onboarding_completed
    )

    route, method = (
        find_identity_update_route()
    )

    response = client.request(
        method.upper(),
        route,
        json={
            "name": "Updated Test User",
        },
    )

    assert response.status_code in {
        200,
        204,
    }

    db_session.expire_all()

    user_after = (
        db_session.query(models.User)
        .filter(models.User.id == 1)
        .first()
    )

    assert user_after is not None

    assert (
        user_after.name
        == "Updated Test User"
    )

    assert (
        user_after.gender
        == original_gender
    )

    assert (
        user_after.age
        == original_age
    )

    assert (
        user_after.onboarding_completed
        == original_onboarding_status
    )