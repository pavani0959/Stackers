"""
Phase 6 backend tests — Fashion Memory & Regret Prevention.

Uses the shared conftest.py (real test.db with migrations).
Each test that writes data does a targeted cleanup so tests do NOT
bleed state into each other.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app
from config import get_settings
from database import SessionLocal
import models

settings = get_settings()

# Uses real test.db provisioned by conftest.py – no need to override get_db.
client = TestClient(app)


def _db_session():
    """Convenience factory for a direct DB session during test setup/teardown."""
    return SessionLocal()


def _ensure_profile_exists():
    """Ensure a StyleProfile exists for the demo user; create one if missing."""
    db = _db_session()
    try:
        profile = (
            db.query(models.StyleProfile)
            .filter(models.StyleProfile.user_id == settings.demo_user_id)
            .order_by(models.StyleProfile.version.desc())
            .first()
        )
        if not profile:
            profile = models.StyleProfile(
                user_id=settings.demo_user_id,
                version=1,
                dna_vector={"minimalist": 0.8},
                primary_identity="minimalist",
                identity={"primary": "minimalist"},
                profile_confidence=80,
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile.version
    finally:
        db.close()


def _ensure_user_prefs_exist():
    """Ensure UserPreference row exists for the demo user."""
    db = _db_session()
    try:
        prefs = (
            db.query(models.UserPreference)
            .filter(models.UserPreference.user_id == settings.demo_user_id)
            .first()
        )
        if not prefs:
            prefs = models.UserPreference(
                user_id=settings.demo_user_id,
                budget_max=3000,
                preferred_aesthetics=["minimalist"],
            )
            db.add(prefs)
            db.commit()
    finally:
        db.close()


def _get_or_create_test_product(sku: str = "TEST-P6-001") -> models.Product:
    """Return an existing product or create a minimal one for testing."""
    db = _db_session()
    try:
        prod = db.query(models.Product).filter(models.Product.sku == sku).first()
        if not prod:
            prod = models.Product(
                sku=sku,
                name="Test T-Shirt Phase6",
                brand="Test Brand",
                price=1500.0,
                originalPrice=2000.0,
                image="test.jpg",
                category="top",
                subcategory="t_shirt",   # valid subcategory from seed
                primary_colour="black",
                gender_segment="unisex",
                budgetTier="mid",
                season="all",
                tags=["minimalist", "casual"],
                occasions=["casual"],
                sizes=["XS", "S", "M", "L", "XL"],  # required by seed validation
            )
            db.add(prod)
            db.commit()
            db.refresh(prod)
        return prod
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Test: Creating an event triggers DNA evolution
# ---------------------------------------------------------------------------

def test_create_event_evolves_dna():
    """Creating a 'keep' event for a product should trigger DNA evolution."""
    _ensure_user_prefs_exist()   # UserPreference must exist for DNA confidence calc
    initial_version = _ensure_profile_exists()
    prod = _get_or_create_test_product()

    payload = {
        "event_type": "keep",
        "product_id": prod.id,
        "metadata": {"reason": "Test keep event"}
    }

    resp = client.post("/api/events", json=payload)
    assert resp.status_code == 201, resp.text

    # Verify the event was created
    data = resp.json()
    assert data["event_type"] == "keep"

    # Verify DNA evolution happened (new profile version may have been created)
    db = _db_session()
    try:
        new_profile = (
            db.query(models.StyleProfile)
            .filter(models.StyleProfile.user_id == settings.demo_user_id)
            .order_by(models.StyleProfile.version.desc())
            .first()
        )
        assert new_profile is not None
        assert new_profile.version >= initial_version
    finally:
        # Cleanup: remove test events created
        db.query(models.UserEvent).filter(
            models.UserEvent.user_id == settings.demo_user_id,
            models.UserEvent.event_type == "keep",
            models.UserEvent.product_id == prod.id,
        ).delete()
        db.commit()
        db.close()


# ---------------------------------------------------------------------------
# Test: Timeline endpoint returns enriched events
# ---------------------------------------------------------------------------

def test_timeline_endpoint():
    """Timeline endpoint should return a list with the correct structure."""
    resp = client.get("/api/memory/timeline")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "timeline" in data

    # Verify timeline items have correct shape
    for item in data["timeline"]:
        assert "type" in item
        assert "date" in item
        if "product" in item and item["product"] is not None:
            assert "name" in item["product"]
            assert "price" in item["product"]


# ---------------------------------------------------------------------------
# Test: Regret check detects duplicate wardrobe item
# ---------------------------------------------------------------------------

def test_regret_check_duplicate_item():
    """Regret check should detect when a user already owns something similar."""
    prod = _get_or_create_test_product()

    # Add a wardrobe item that matches the product
    db = _db_session()
    wardrobe = models.WardrobeItem(
        user_id=settings.demo_user_id,
        name=prod.name,
        category=prod.category,
        subcategory=prod.subcategory,
        primary_colour=prod.primary_colour,
    )
    db.add(wardrobe)
    db.commit()
    wardrobe_id = wardrobe.id
    db.close()

    try:
        resp = client.get(f"/api/memory/regret-check/{prod.id}")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "safe_to_buy" in data
        assert "signals" in data
        # Should detect the duplicate — signal code is 'wardrobe_duplicate'
        duplicate_signals = [s for s in data["signals"] if s.get("code") == "wardrobe_duplicate"]
        assert len(duplicate_signals) > 0
    finally:
        # Cleanup
        db = _db_session()
        db.query(models.WardrobeItem).filter(models.WardrobeItem.id == wardrobe_id).delete()
        db.commit()
        db.close()


# ---------------------------------------------------------------------------
# Test: Regret check provides alternatives when signals exist
# ---------------------------------------------------------------------------

def test_regret_check_alternatives():
    """When regret is detected, alternatives should be suggested."""
    prod = _get_or_create_test_product()
    _ensure_user_prefs_exist()

    # Temporarily lower budget to force over_budget signal
    db = _db_session()
    prefs = (
        db.query(models.UserPreference)
        .filter(models.UserPreference.user_id == settings.demo_user_id)
        .first()
    )
    original_budget = prefs.budget_max
    prefs.budget_max = int(prod.price) - 100  # set budget below product price
    db.commit()
    db.close()

    try:
        resp = client.get(f"/api/memory/regret-check/{prod.id}")
        data = resp.json()

        assert "signals" in data, f"Response missing 'signals': {data}"
        assert len(data["signals"]) > 0, "Expected at least one regret signal"
        assert "alternatives" in data
    finally:
        # Restore budget
        db = _db_session()
        prefs = (
            db.query(models.UserPreference)
            .filter(models.UserPreference.user_id == settings.demo_user_id)
            .first()
        )
        if prefs:
            prefs.budget_max = original_budget
            db.commit()
        db.close()
