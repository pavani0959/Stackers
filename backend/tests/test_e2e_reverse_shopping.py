import pytest
from fastapi.testclient import TestClient
from main import app

def test_reverse_shopping_e2e():
    client = TestClient(app)
    
    response = client.post(
        "/api/recommend/reverse", 
        json={"prompt": "Interview tomorrow under 2k"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["within_budget"] == True
    assert data["parsed_intent"]["budget_total"] == 2000
    assert "outfits" in data
    assert len(data["outfits"]) > 0

