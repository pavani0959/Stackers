import httpx
import pytest

from main import app


@pytest.mark.anyio
async def test_health_check() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        res_live = await client.get("/api/health/live")
        res_ready = await client.get("/api/health/ready")

    assert res_live.status_code == 200
    assert res_live.json()["status"] == "ok"
    
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"


@pytest.mark.anyio
async def test_validation_errors_use_shared_shape() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post("/api/dna/calculate", json={"tags": "not-a-list"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
