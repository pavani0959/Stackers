from __future__ import annotations

import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from config import get_settings
from database import SessionLocal
from main import app
from models import (
    Product,
    StyleProfile,
    UserEvent,
    WardrobeItem,
)


client = TestClient(app)

STYLE_TOKENS = (
    "minimal",
    "street",
    "casual",
    "luxury",
    "y2k",
)


def _snapshot_user_state(
    user_id: int,
) -> dict[str, set[int]]:
    db = SessionLocal()

    try:
        return {
            "event_ids": {
                event_id
                for (event_id,) in (
                    db.query(UserEvent.id)
                    .filter(
                        UserEvent.user_id
                        == user_id
                    )
                    .all()
                )
            },
            "wardrobe_ids": {
                wardrobe_id
                for (wardrobe_id,) in (
                    db.query(WardrobeItem.id)
                    .filter(
                        WardrobeItem.user_id
                        == user_id
                    )
                    .all()
                )
            },
            "profile_ids": {
                profile_id
                for (profile_id,) in (
                    db.query(StyleProfile.id)
                    .filter(
                        StyleProfile.user_id
                        == user_id
                    )
                    .all()
                )
            },
        }
    finally:
        db.close()


def _delete_rows_created_after(
    *,
    user_id: int,
    snapshot: dict[str, set[int]],
) -> None:
    db = SessionLocal()

    try:
        event_query = (
            db.query(UserEvent)
            .filter(
                UserEvent.user_id
                == user_id
            )
        )

        if snapshot["event_ids"]:
            event_query = event_query.filter(
                UserEvent.id.not_in(
                    snapshot["event_ids"]
                )
            )

        event_query.delete(
            synchronize_session=False,
        )

        wardrobe_query = (
            db.query(WardrobeItem)
            .filter(
                WardrobeItem.user_id
                == user_id
            )
        )

        if snapshot["wardrobe_ids"]:
            wardrobe_query = (
                wardrobe_query.filter(
                    WardrobeItem.id.not_in(
                        snapshot[
                            "wardrobe_ids"
                        ]
                    )
                )
            )

        wardrobe_query.delete(
            synchronize_session=False,
        )

        profile_query = (
            db.query(StyleProfile)
            .filter(
                StyleProfile.user_id
                == user_id
            )
        )

        if snapshot["profile_ids"]:
            profile_query = (
                profile_query.filter(
                    StyleProfile.id.not_in(
                        snapshot[
                            "profile_ids"
                        ]
                    )
                )
            )

        profile_query.delete(
            synchronize_session=False,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


@pytest.fixture
def isolated_demo_user_state():
    settings = get_settings()
    user_id = settings.demo_user_id

    snapshot = _snapshot_user_state(
        user_id,
    )

    yield user_id

    _delete_rows_created_after(
        user_id=user_id,
        snapshot=snapshot,
    )


def _latest_profile(
    user_id: int,
) -> StyleProfile | None:
    db = SessionLocal()

    try:
        return (
            db.query(StyleProfile)
            .filter(
                StyleProfile.user_id
                == user_id
            )
            .order_by(
                StyleProfile.version.desc()
            )
            .first()
        )
    finally:
        db.close()


def _ensure_profile(
    user_id: int,
) -> StyleProfile:
    existing = _latest_profile(
        user_id,
    )

    if existing is not None:
        return existing

    db = SessionLocal()

    try:
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
                "phase6-strict-test"
            ),
            identity={
                "name": "Minimalist",
                "description": (
                    "Strict Phase 6 test profile."
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
            },
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

        return profile

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def _choose_unowned_product(
    user_id: int,
) -> Product:
    db = SessionLocal()

    try:
        owned_product_ids = {
            product_id
            for (product_id,) in (
                db.query(
                    WardrobeItem.product_id
                )
                .filter(
                    WardrobeItem.user_id
                    == user_id,
                    WardrobeItem.product_id.is_not(
                        None
                    ),
                )
                .all()
            )
        }

        query = (
            db.query(Product)
            .filter(
                Product.is_active.is_(
                    True
                )
            )
            .order_by(Product.id)
        )

        if owned_product_ids:
            query = query.filter(
                Product.id.not_in(
                    owned_product_ids
                )
            )

        products = query.all()

        if not products:
            raise AssertionError(
                "No unowned active product "
                "is available for the test."
            )

        for product in products:
            searchable_text = " ".join(
                [
                    *(
                        product.tags
                        or []
                    ),
                    product.category
                    or "",
                    product.subcategory
                    or "",
                    product.description
                    or "",
                ]
            ).lower()

            if any(
                token in searchable_text
                for token in STYLE_TOKENS
            ):
                return product

        return products[0]

    finally:
        db.close()


def test_complete_purchase_lifecycle(
    isolated_demo_user_state,
):
    user_id = isolated_demo_user_state
    product = _choose_unowned_product(
        user_id,
    )

    db = SessionLocal()

    try:
        wardrobe_count_before = (
            db.query(WardrobeItem)
            .filter(
                WardrobeItem.user_id
                == user_id
            )
            .count()
        )
    finally:
        db.close()

    # Adding to cart records intent only.
    cart_response = client.post(
        "/api/events",
        json={
            "event_type": "cart_add",
            "product_id": product.id,
            "metadata": {
                "source": (
                    "phase6_strict_test"
                ),
                "size": "M",
            },
        },
    )

    assert cart_response.status_code in {
        200,
        201,
    }

    db = SessionLocal()

    try:
        wardrobe_count_after_cart = (
            db.query(WardrobeItem)
            .filter(
                WardrobeItem.user_id
                == user_id
            )
            .count()
        )
    finally:
        db.close()

    assert (
        wardrobe_count_after_cart
        == wardrobe_count_before
    )

    # Checkout creates the purchase and wardrobe.
    checkout_response = client.post(
        "/api/memory/checkout",
        json={
            "items": [
                {
                    "product_id": product.id,
                    "size": "M",
                    "recommendation_item_id": (
                        None
                    ),
                    "decision_snapshot_id": (
                        None
                    ),
                }
            ]
        },
    )

    assert checkout_response.status_code == 200

    checkout_data = (
        checkout_response.json()
    )

    assert len(
        checkout_data[
            "purchase_event_ids"
        ]
    ) == 1

    assert len(
        checkout_data[
            "wardrobe_item_ids"
        ]
    ) == 1

    purchase_event_id = (
        checkout_data[
            "purchase_event_ids"
        ][0]
    )

    wardrobe_item_id = (
        checkout_data[
            "wardrobe_item_ids"
        ][0]
    )

    db = SessionLocal()

    try:
        purchase_event = db.get(
            UserEvent,
            purchase_event_id,
        )

        wardrobe_item = db.get(
            WardrobeItem,
            wardrobe_item_id,
        )

        assert purchase_event is not None
        assert (
            purchase_event.event_type
            == "purchase"
        )
        assert (
            purchase_event.product_id
            == product.id
        )
        assert (
            purchase_event.wardrobe_item_id
            == wardrobe_item_id
        )

        assert wardrobe_item is not None
        assert wardrobe_item.is_active is True
        assert (
            wardrobe_item.product_id
            == product.id
        )
        assert (
            wardrobe_item.source
            == "purchase"
        )
    finally:
        db.close()

    # Purchase appears in memory.
    timeline_response = client.get(
        "/api/memory/timeline"
    )

    assert timeline_response.status_code == 200

    timeline_text = json.dumps(
        timeline_response.json(),
    ).lower()

    assert "purchase" in timeline_text

    # Keep creates a keep event.
    keep_response = client.post(
        (
            "/api/memory/items/"
            f"{wardrobe_item_id}/keep"
        ),
        json={
            "reason": (
                "Fits the planned wardrobe."
            )
        },
    )

    assert keep_response.status_code == 200

    keep_data = keep_response.json()

    assert keep_data["event_type"] == "keep"
    assert (
        keep_data["wardrobe_item_id"]
        == wardrobe_item_id
    )

    db = SessionLocal()

    try:
        keep_event = db.get(
            UserEvent,
            keep_data["event_id"],
        )

        assert keep_event is not None
        assert keep_event.event_type == "keep"
    finally:
        db.close()

    # Return creates a return event and
    # deactivates the wardrobe item.
    return_response = client.post(
        (
            "/api/memory/items/"
            f"{wardrobe_item_id}/return"
        ),
        json={
            "reason": (
                "Did not work with the wardrobe."
            )
        },
    )

    assert return_response.status_code == 200

    return_data = return_response.json()

    assert (
        return_data["event_type"]
        == "return"
    )

    db = SessionLocal()

    try:
        returned_item = db.get(
            WardrobeItem,
            wardrobe_item_id,
        )

        return_event = db.get(
            UserEvent,
            return_data["event_id"],
        )

        assert returned_item is not None
        assert returned_item.is_active is False

        assert return_event is not None
        assert (
            return_event.event_type
            == "return"
        )
    finally:
        db.close()


def test_one_return_creates_exactly_one_material_dna_version(
    isolated_demo_user_state,
):
    user_id = isolated_demo_user_state

    _ensure_profile(user_id)

    product = _choose_unowned_product(
        user_id,
    )

    checkout_response = client.post(
        "/api/memory/checkout",
        json={
            "items": [
                {
                    "product_id": product.id,
                    "size": "M",
                }
            ]
        },
    )

    assert checkout_response.status_code == 200

    wardrobe_item_id = (
        checkout_response.json()[
            "wardrobe_item_ids"
        ][0]
    )

    db = SessionLocal()

    try:
        initial_profile = (
            db.query(StyleProfile)
            .filter(
                StyleProfile.user_id
                == user_id
            )
            .order_by(
                StyleProfile.version.desc()
            )
            .first()
        )

        assert initial_profile is not None

        initial_version = (
            initial_profile.version
        )

        initial_dna = dict(
            initial_profile.dna_vector
            or {}
        )
    finally:
        db.close()

    response = client.post(
        (
            "/api/memory/items/"
            f"{wardrobe_item_id}/return"
        ),
        json={
            "reason": (
                "Strict DNA evolution test."
            )
        },
    )

    assert response.status_code == 200

    db = SessionLocal()

    try:
        new_profile = (
            db.query(StyleProfile)
            .filter(
                StyleProfile.user_id
                == user_id
            )
            .order_by(
                StyleProfile.version.desc()
            )
            .first()
        )

        assert new_profile is not None

        assert (
            new_profile.version
            == initial_version + 1
        )

        assert any(
            abs(
                new_profile.dna_vector[key]
                - initial_dna.get(key, 0)
            )
            >= 0.1
            for key in (
                new_profile.dna_vector
                or {}
            )
        )
    finally:
        db.close()


def test_recommendation_accept_metadata_is_persisted(
    isolated_demo_user_state,
):
    user_id = isolated_demo_user_state

    db = SessionLocal()

    try:
        products = (
            db.query(Product)
            .filter(
                Product.is_active.is_(
                    True
                )
            )
            .order_by(Product.id)
            .limit(2)
            .all()
        )
    finally:
        db.close()

    assert len(products) == 2

    original_product = products[0]
    alternative = products[1]

    response = client.post(
        "/api/events",
        json={
            "event_type": (
                "recommendation_accept"
            ),
            "product_id": alternative.id,
            "metadata": {
                "decision_changed": True,
                "rejected_product_id": (
                    original_product.id
                ),
                "alternative_product_id": (
                    alternative.id
                ),
                "regret_signal_codes": [
                    "wardrobe_duplicate",
                ],
            },
        },
    )

    assert response.status_code in {
        200,
        201,
    }

    event_id = response.json()["id"]

    db = SessionLocal()

    try:
        event = db.get(
            UserEvent,
            event_id,
        )

        assert event is not None

        assert (
            event.event_type
            == "recommendation_accept"
        )

        assert (
            event.product_id
            == alternative.id
        )

        assert (
            event.event_metadata[
                "decision_changed"
            ]
            is True
        )

        assert (
            event.event_metadata[
                "rejected_product_id"
            ]
            == original_product.id
        )

        assert (
            event.event_metadata[
                "alternative_product_id"
            ]
            == alternative.id
        )

        assert (
            event.event_metadata[
                "regret_signal_codes"
            ]
            == [
                "wardrobe_duplicate",
            ]
        )
    finally:
        db.close()
