import httpx
import pytest

from main import app


@pytest.mark.anyio
async def test_missing_product_uses_shared_404_shape() -> None:
    transport = httpx.ASGITransport(
        app=app,
        raise_app_exceptions=False,
    )
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/decisions/products/999999",
            json={"context": {}},
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert response.json()["error"]["message"] == "Product not found"
