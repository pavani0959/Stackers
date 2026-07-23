from __future__ import annotations

from copy import deepcopy
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models
from database import Base, get_db
from main import app
from services.decision_score_calculator import DecisionScoreCalculator


TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture()
def db_session():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    user = models.User(
        id=1,
        seed_key="phase4-test-user",
        name="Decision Test User",
        email="phase4@example.com",
        gender="women",
        age=21,
        onboarding_completed=True,
        is_synthetic=False,
    )
    session.add(user)
    session.flush()

    session.add(
        models.UserPreference(
            user_id=user.id,
            budget_min=800,
            budget_max=3000,
            budget_tier="mid_range",
            preferred_colours=["black", "white"],
            preferred_brands=[],
            preferred_occasions=["campus"],
            preferred_aesthetics=["minimalist"],
            fit_preferences=["relaxed"],
            occasion_priorities={"campus": 1.0},
        )
    )
    session.add(
        models.StyleProfile(
            user_id=user.id,
            version=1,
            dna_vector={"minimalist": 50.0, "streetwear": 50.0},
            primary_identity="minimalist",
            secondary_identity="streetwear",
            profile_confidence=86,
            source="test",
            model_version="dna-v1",
            identity={
                "name": "Minimalist Explorer",
                "description": "Test identity",
                "primary": "minimalist",
                "secondary": "streetwear",
            },
            confidence_breakdown={},
            evidence={},
        )
    )
    session.add_all(
        [
            models.Product(
                id=1,
                sku="PHASE4-001",
                name="Minimal Campus Shirt",
                brand="Test Brand",
                description="Minimal casual shirt",
                price=1499,
                originalPrice=1999,
                image="https://example.com/shirt.jpg",
                category="top",
                subcategory="shirt",
                primary_colour="white",
                gender_segment="women",
                tags=["minimalist", "casual"],
                occasions=["campus", "casual"],
                sizes=["S", "M", "L"],
                budgetTier="mid_range",
                season="all_season",
                stock_quantity=10,
                is_active=True,
            ),
            models.Product(
                id=2,
                sku="PHASE4-002",
                name="Premium Black Cargo",
                brand="Test Brand",
                description="Streetwear cargo trousers",
                price=4200,
                originalPrice=5000,
                image="https://example.com/cargo.jpg",
                category="bottom",
                subcategory="cargo_pants",
                primary_colour="black",
                gender_segment="women",
                tags=["streetwear", "bold"],
                occasions=["party"],
                sizes=["S", "M", "L"],
                budgetTier="premium",
                season="winter",
                stock_quantity=10,
                is_active=True,
            ),
            models.Product(
                id=3,
                sku="PHASE4-003",
                name="Streetwear Cargo Tie",
                brand="Test Brand",
                description="Streetwear cargo trousers",
                price=1499,
                originalPrice=1999,
                image="https://example.com/cargo3.jpg",
                category="bottom",
                subcategory="cargo_pants",
                primary_colour="black",
                gender_segment="women",
                tags=["streetwear", "bold"],
                occasions=["campus", "party"],
                sizes=["S", "M", "L"],
                budgetTier="mid_range",
                season="all_season",
                stock_quantity=10,
                is_active=True,
            ),
        ]
    )
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_decision(client: TestClient, product_id: int = 1):
    return client.post(
        f"/api/decisions/products/{product_id}",
        json={
            "context": {
                "occasion": "campus",
                "season": "summer",
                "source": "ignored-client-value",
            }
        },
    )


def test_every_score_is_valid_and_traceable(client):
    response = create_decision(client)
    assert response.status_code == 201, response.text
    payload = response.json()

    assert 0 <= payload["overall_score"] <= 100
    for component in payload["score_breakdown"].values():
        assert 0 <= component["score"] <= 100
        assert 0 <= component["weight"] <= 1
        assert component["evidence_source"]
        assert isinstance(component["evidence"], dict)

    expected = round(
        sum(
            component["weighted_score"]
            for component in payload["score_breakdown"].values()
        )
    )
    assert payload["overall_score"] == expected


def test_server_rejects_frontend_owned_profile_fields(client):
    response = client.post(
        "/api/decisions/products/1",
        json={
            "user_profile": {"dna": {"minimalist": 100}},
            "dna": {"minimalist": 100},
            "confidence": 100,
            "score_breakdown": {},
            "context": {},
        },
    )
    assert response.status_code == 422


def test_snapshot_is_persisted_and_read_by_uuid(client, db_session):
    created = create_decision(client).json()
    snapshot_id = UUID(created["snapshot_id"])

    db_session.expire_all()
    saved = (
        db_session.query(models.RecommendationItem)
        .filter(models.RecommendationItem.snapshot_id == snapshot_id)
        .one()
    )
    assert saved.product_snapshot["price"] == 1499
    assert saved.session.profile_version == 1
    assert saved.session.model_version == "decision-v1.0.0"

    fetched = client.get(f"/api/decisions/{snapshot_id}")
    assert fetched.status_code == 200
    assert fetched.json() == created


def test_old_snapshot_does_not_change_after_profile_change(client, db_session):
    created = create_decision(client).json()
    original_score = created["overall_score"]
    original_explanation = deepcopy(created["explanation"])

    db_session.add(
        models.StyleProfile(
            user_id=1,
            version=2,
            dna_vector={"y2k": 100.0},
            primary_identity="y2k",
            secondary_identity=None,
            profile_confidence=90,
            source="test",
            model_version="dna-v1",
            identity={
                "name": "Y2K Explorer",
                "description": "Changed identity",
                "primary": "y2k",
                "secondary": None,
            },
            confidence_breakdown={},
            evidence={},
        )
    )
    db_session.commit()

    fetched = client.get(
        f"/api/decisions/{created['snapshot_id']}",
    ).json()
    assert fetched["overall_score"] == original_score
    assert fetched["explanation"] == original_explanation
    assert fetched["profile_version"] == 1


def test_old_snapshot_does_not_change_after_product_change(client, db_session):
    created = create_decision(client).json()
    original_product = deepcopy(created["product"])
    original_explanation = deepcopy(created["explanation"])

    product = db_session.get(models.Product, 1)
    product.price = 9999
    product.tags = ["y2k"]
    db_session.commit()

    fetched = client.get(
        f"/api/decisions/{created['snapshot_id']}",
    ).json()
    assert fetched["product"] == original_product
    assert fetched["explanation"] == original_explanation


def test_regret_signals_use_real_evidence(client, db_session):
    db_session.add(
        models.WardrobeItem(
            user_id=1,
            source="purchase",
            name="Existing Black Cargo",
            category="bottom",
            subcategory="cargo_pants",
            primary_colour="black",
            tags=["streetwear"],
            is_active=True,
        )
    )
    db_session.commit()

    response = create_decision(client, product_id=2)
    assert response.status_code == 201
    signals = {
        signal["code"]: signal
        for signal in response.json()["regret_signals"]
    }
    assert signals["over_budget"]["evidence"]["over_budget_by"] == 1200
    assert signals["wardrobe_duplicate"]["evidence"]["duplicate_count"] == 1

    within_budget = create_decision(client, product_id=1).json()
    assert "over_budget" not in {
        signal["code"] for signal in within_budget["regret_signals"]
    }


def test_response_contains_no_unsupported_community_claims(client):
    serialized = create_decision(client).text.lower()
    forbidden = [
        "similar users",
        "users loved",
        "90% of users",
        "bought in the last 7 days",
        "real eyes",
        "returned 60%",
    ]
    for phrase in forbidden:
        assert phrase not in serialized


def test_memory_returns_stored_snapshot_without_recalculation(
    client,
    db_session,
    monkeypatch,
):
    created = create_decision(client).json()
    db_session.add(
        models.UserEvent(
            user_id=1,
            product_id=created["product"]["id"],
            recommendation_item_id=created["recommendation_item_id"],
            event_type="purchase",
            event_metadata={"checkout_id": "test-checkout"},
        )
    )
    db_session.commit()

    def fail_if_called(*args, **kwargs):
        del args, kwargs
        raise AssertionError("Memory must not recalculate a score")

    monkeypatch.setattr(
        DecisionScoreCalculator,
        "calculate",
        fail_if_called,
    )

    response = client.get("/api/decisions/memory")
    assert response.status_code == 200, response.text
    memory = response.json()["items"]
    assert len(memory) == 1
    assert memory[0]["decision"]["snapshot_id"] == created["snapshot_id"]
    assert memory[0]["decision"]["overall_score"] == created["overall_score"]
    assert memory[0]["event"]["event_type"] == "purchase"


def test_feed_uses_one_session_and_persists_ranked_items(client, db_session):
    response = client.post(
        "/api/decisions/feed",
        json={
            "limit": 2,
            "anti_trend": False,
            "context": {
                "occasion": "campus",
                "season": "summer",
            },
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert len(payload["items"]) == 2
    assert {
        item["session_id"] for item in payload["items"]
    } == {payload["session_id"]}

    ranks = (
        db_session.query(models.RecommendationItem.rank)
        .filter(
            models.RecommendationItem.session_id == payload["session_id"],
        )
        .order_by(models.RecommendationItem.rank)
        .all()
    )
    assert [rank for (rank,) in ranks] == [1, 2]


def test_feed_vibe_re_ranks_products(client, db_session):
    # Quiet vibe biases towards 'minimalist' (PHASE4-001)
    quiet_response = client.post(
        "/api/decisions/feed",
        json={
            "limit": 2,
            "anti_trend": False,
            "context": {
                "occasion": "campus",
                "vibe": "quiet",
            },
        },
    )
    quiet_payload = quiet_response.json()
    
    # Bold vibe biases towards 'streetwear' and 'bold' (PHASE4-002)
    bold_response = client.post(
        "/api/decisions/feed",
        json={
            "limit": 2,
            "anti_trend": False,
            "context": {
                "occasion": "campus",
                "vibe": "bold",
            },
        },
    )
    bold_payload = bold_response.json()

    # The top ranked product should be different for each vibe
    quiet_top_sku = quiet_payload["items"][0]["product"]["sku"]
    bold_top_sku = bold_payload["items"][0]["product"]["sku"]

    print("QUIET SCORES:")
    for item in quiet_payload["items"]:
        print(f"  {item['product']['sku']}: {item['overall_score']}")

    print("BOLD SCORES:")
    for item in bold_payload["items"]:
        print(f"  {item['product']['sku']}: {item['overall_score']} -> {item['score_breakdown']['vibe']['score']} (Vibe component score)")
    
    assert quiet_top_sku != bold_top_sku
    assert quiet_top_sku == "PHASE4-001"
    assert bold_top_sku == "PHASE4-003"
