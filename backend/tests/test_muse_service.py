import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from main import app
from config import get_settings
from database import SessionLocal
import models
from services.muse_service import MuseService

# Use the seed_reverse_server_profile fixture by making sure this file's name is handled 
# or by explicitly doing the DB setup. Actually, let's just use the TestClient.
# Since we need real DB rows for a seeded test user, we can write a fixture or use the one from conftest
# However, conftest.py's seed_reverse_server_profile only triggers for specific file names.
# Let's mock DB or we can insert data.
# The `migrated_test_database` fixture in conftest.py seeds 120 products and User 1.
# But it does not seed the style profile and preferences unless we use `seed_reverse_server_profile`.
# We'll just create the data if missing.

@pytest.fixture(autouse=True)
def setup_test_data():
    db = SessionLocal()
    settings = get_settings()
    user = db.query(models.User).filter(models.User.id == settings.demo_user_id).first()
    if user:
        prefs = db.query(models.UserPreference).filter(models.UserPreference.user_id == user.id).first()
        if not prefs:
            prefs = models.UserPreference(
                user_id=user.id,
                budget_min=500,
                budget_max=3000,
                budget_tier="campus-casual",
                preferred_occasions=["campus"],
                preferred_aesthetics=["minimalist"],
                fit_preferences=["regular"],
                comfort_priority=0.5,
                trend_openness=0.5,
                fashion_goal="smart-shopping",
                comfort_expression_balance=0.5,
                occasion_priorities={"campus": 1.0}
            )
            db.add(prefs)
        
        prof = db.query(models.StyleProfile).filter(models.StyleProfile.user_id == user.id).first()
        if not prof:
            import uuid
            prof = models.StyleProfile(
                profile_id=uuid.uuid4(),
                user_id=user.id,
                version=1,
                dna_vector={"minimalist": 100},
                primary_identity="Minimalist",
                profile_confidence=100,
                source="pytest",
                model_version="v1",
                identity={"name": "Minimalist"},
                evidence={"source": "pytest", "answer_count": 8},
                confidence_breakdown={"quiz_completeness": 100}
            )
            db.add(prof)
        db.commit()
    db.close()
    yield
    # We could clean up, but DB is rebuilt per session anyway.

def test_muse_fallback_no_api_key():
    settings = get_settings()
    original_key = settings.gemini_api_key
    settings.gemini_api_key = None
    try:
        client = TestClient(app)
        response = client.post(
            "/api/muse/chat", 
            json={"message": "hello", "user_profile": {"name": "Test"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert data["intent"] == "greeting"  # Fallback logic handles greeting
    finally:
        settings.gemini_api_key = original_key

@patch("services.muse_service.genai")
def test_muse_service_grounded_context_and_success(mock_genai):
    settings = get_settings()
    settings.gemini_api_key = "test_fake_key"
    
    mock_client = MagicMock()
    mock_genai.Client.return_value = mock_client
    
    # Mock a valid JSON response from Gemini
    mock_response = MagicMock()
    mock_response.text = '{"reply": "Here is a recommendation", "recommended_product_ids": [1], "intent": "recommendation"}'
    mock_client.models.generate_content.return_value = mock_response
    
    client = TestClient(app)
    response = client.post(
        "/api/muse/chat", 
        json={"message": "recommend something", "user_profile": {"name": "Test"}}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Here is a recommendation"
    assert data["intent"] == "recommendation"
    # Products might be empty if product ID 1 is not in top 15, but it won't crash
    assert "recommendations" in data

    # Verify context built and sent
    mock_client.models.generate_content.assert_called_once()
    args, kwargs = mock_client.models.generate_content.call_args
    system_instruction = kwargs["config"]["system_instruction"]
    assert "User DNA Vector:" in system_instruction
    assert "Wardrobe Items:" in system_instruction
    assert "CANDIDATE PRODUCTS:" in system_instruction
    
    settings.gemini_api_key = None

@patch("services.muse_service.genai")
def test_muse_service_malformed_model_output(mock_genai):
    settings = get_settings()
    settings.gemini_api_key = "test_fake_key"
    
    mock_client = MagicMock()
    mock_genai.Client.return_value = mock_client
    
    # Mock a malformed JSON response
    mock_response = MagicMock()
    mock_response.text = '{"reply": "Oops, missing required fields"}'
    mock_client.models.generate_content.return_value = mock_response
    
    client = TestClient(app)
    response = client.post(
        "/api/muse/chat", 
        json={"message": "recommend something", "user_profile": {"name": "Test"}}
    )
    
    # It should not crash, it should fall back to rule-based
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    
    settings.gemini_api_key = None
