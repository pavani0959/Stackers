import httpx
import pytest

from main import app


@pytest.mark.anyio
async def test_missing_product_uses_shared_404_shape() -> None:
    transport = httpx.ASGITransport(
        app=app,
        raise_app_exceptions=False,
    )

    payload = {
        "user_profile": {
            "name": "Test User",
            "identityName": "Minimalist",
            "dna": {
                "minimalist": 70,
                "streetwear": 30,
            },
            "occasions": ["campus"],
            "budget": "campus-casual",
            "purchaseMemory": [],
        }
    }

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/recommend/confidence/999999",
            json=payload,
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert response.json()["error"]["message"] == "Product not found"