import httpx
import pytest

from main import app


@pytest.mark.anyio
async def test_profile_is_persisted() -> None:
    transport = httpx.ASGITransport(
        app=app,
        raise_app_exceptions=False,
    )

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        update_response = await client.put(
            "/api/profile/preferences",
            json={
                "budget_min": 800,
                "budget_max": 3000,
                "budget_tier": "mid_range",
                "preferred_colours": [
                    "black",
                    "white",
                ],
                "preferred_brands": [],
                "preferred_occasions": [
                    "campus"
                ],
                "preferred_aesthetics": [
                    "minimalist"
                ],
                "fit_preferences": [
                    "relaxed"
                ],
                "comfort_priority": 0.8,
                "trend_openness": 0.4,
            },
        )

        assert update_response.status_code == 200

        profile_response = await client.get(
            "/api/profile"
        )

    assert profile_response.status_code == 200

    payload = profile_response.json()

    assert (
        payload["preferences"]["budget_min"]
        == 800
    )
    assert payload["user"]["onboarding_completed"]

@pytest.mark.anyio
async def test_dna_creates_new_versions() -> None:
    transport = httpx.ASGITransport(
        app=app,
        raise_app_exceptions=False,
    )

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        first = await client.post(
            "/api/profile/dna",
            json={
                "dna_vector": {
                    "minimalist": 70,
                    "streetwear": 30,
                },
                "primary_identity": "minimalist",
                "secondary_identity": "streetwear",
                "profile_confidence": 70,
                "source": "test",
                "model_version": "dna-v1",
            },
        )

        second = await client.post(
            "/api/profile/dna",
            json={
                "dna_vector": {
                    "minimalist": 60,
                    "streetwear": 40,
                },
                "primary_identity": "minimalist",
                "secondary_identity": "streetwear",
                "profile_confidence": 75,
                "source": "test",
                "model_version": "dna-v1",
            },
        )

    assert first.status_code == 201
    assert second.status_code == 201
    assert (
        second.json()["version"]
        == first.json()["version"] + 1
    )