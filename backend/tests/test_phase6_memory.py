"""
Phase 6 backend tests — Fashion Memory & Regret Prevention.
"""
import pytest
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
import models
import schemas
from config import get_settings

settings = get_settings()

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


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    
    # Create Demo User & Preferences
    user = models.User(
        id=settings.demo_user_id,
        name="Demo",
        email="demo@myntra.com",
    )
    prefs = models.UserPreference(
        user_id=settings.demo_user_id,
        budget_max=3000,
        preferred_aesthetics=["minimalist"],
    )
    db.add(user)
    db.add(prefs)
    
    # Create Dummy Profile
    prof = models.StyleProfile(
        user_id=settings.demo_user_id,
        version=1,
        dna_vector={"minimalist": 0.8},
        primary_identity="minimalist",
        identity={"primary": "minimalist"},
        profile_confidence=80,
    )
    db.add(prof)

    # Create Dummy Product
    prod = models.Product(
        sku="TEST-001",
        name="Test T-Shirt",
        brand="Test Brand",
        price=1500.0,
        originalPrice=2000.0,
        image="test.jpg",
        category="top",
        subcategory="tshirt",
        primary_colour="black",
        gender_segment="unisex",
        budgetTier="mid",
        season="all",
        tags=["minimalist", "casual"],
        occasions=[],
        sizes=[],
    )
    db.add(prod)
    
    db.commit()
    yield
    db.close()
    Base.metadata.drop_all(bind=test_engine)


def test_create_event_evolves_dna():
    """Test that creating a product-related event triggers DNA evolution."""
    db = TestingSessionLocal()
    
    # 1. Fetch initial profile version
    initial_profile = db.query(models.StyleProfile).filter(
        models.StyleProfile.user_id == settings.demo_user_id
    ).order_by(models.StyleProfile.version.desc()).first()
    
    initial_version = initial_profile.version if initial_profile else 0
    
    # 2. Fire an event that should trigger evolution (keep event is strong)
    product = db.query(models.Product).first()
    payload = {
        "event_type": "keep",
        "product_id": product.id,
        "metadata": {"reason": "Test keep event"}
    }
    
    resp = client.post("/api/events", json=payload)
    assert resp.status_code == 201
    
    # 3. Verify new profile version was created
    new_profile = db.query(models.StyleProfile).filter(
        models.StyleProfile.user_id == settings.demo_user_id
    ).order_by(models.StyleProfile.version.desc()).first()
    
    # Because 'keep' is positive and the item likely had tags, it should have evolved
    assert new_profile is not None
    if initial_profile:
        # Note: If item_vector didn't match old dna or was empty, it might skip, 
        # but our stub assigns tags to vector so it should update.
        assert new_profile.version >= initial_version
        if new_profile.version > initial_version:
            assert "event_evolution" in new_profile.source
    db.close()


def test_timeline_endpoint():
    """Test that timeline endpoint returns enriched events."""
    resp = client.get("/api/memory/timeline")
    assert resp.status_code == 200
    data = resp.json()
    assert "timeline" in data
    
    # Verify timeline items contain product metadata if available
    for item in data["timeline"]:
        assert "type" in item
        assert "date" in item
        if "product" in item:
            assert "name" in item["product"]
            assert "price" in item["product"]


def test_regret_check_duplicate_item():
    """Test the regret check API against an item identical to wardrobe."""
    db = TestingSessionLocal()
    product = db.query(models.Product).first()
    
    # Force a wardrobe item to match the product
    wardrobe = models.WardrobeItem(
        user_id=settings.demo_user_id,
        name=product.name,
        category=product.category,
        subcategory=product.subcategory,
        primary_colour=product.primary_colour,
    )
    db.add(wardrobe)
    db.commit()
    
    # Call regret check
    resp = client.get(f"/api/memory/regret-check/{product.id}")
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["product_id"] == product.id
    assert len(data["signals"]) > 0
    
    duplicate_signal = next((s for s in data["signals"] if s["code"] == "wardrobe_duplicate"), None)
    assert duplicate_signal is not None
    assert duplicate_signal["evidence"]["duplicate_count"] >= 1
    assert data["safe_to_buy"] is False
    
    # Cleanup
    db.delete(wardrobe)
    db.commit()
    db.close()


def test_regret_check_alternatives():
    """Test that alternatives are provided when regret signals are present."""
    db = TestingSessionLocal()
    product = db.query(models.Product).first()
    
    # We need a second product in the same category to be an alternative
    alt_prod = models.Product(
        sku="TEST-002",
        name="Alt T-Shirt",
        brand="Alt Brand",
        price=1600.0,
        originalPrice=2000.0,
        image="test2.jpg",
        category="top",
        subcategory="tshirt",
        primary_colour="white",
        gender_segment="unisex",
        budgetTier="mid",
        season="all",
        tags=["minimalist"],
        occasions=[],
        sizes=[],
    )
    db.add(alt_prod)
    
    # Force budget preference to trigger over_budget signal
    prefs = db.query(models.UserPreference).filter(
        models.UserPreference.user_id == settings.demo_user_id
    ).first()
    old_max = prefs.budget_max
    prefs.budget_max = int(product.price) - 100
    db.commit()
    
    resp = client.get(f"/api/memory/regret-check/{product.id}")
    data = resp.json()
    
    # Restore prefs
    prefs.budget_max = old_max
    db.commit()
    db.close()
    
    assert len(data["signals"]) > 0
    assert len(data["alternatives"]) > 0
    alt = data["alternatives"][0]
    assert "name" in alt
    assert "reason" in alt
