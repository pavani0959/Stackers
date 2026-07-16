from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_reverse_fastapi():
    payload = {
        "prompt": "Interview tomorrow under 2k",
        "user_profile": {
            "id": 1,
            "name": "Bhavika",
            "email": "demo@myntra.com",
            "gender": "women",
            "age": 20,
            "onboarding_completed": True,
            "dna": {"minimalist": 80},
            "occasions": ["work"],
            "budget": "premium"
        }
    }
    response = client.post("/api/recommend/reverse", json=payload)
    print(response.json())
    assert response.status_code == 200

