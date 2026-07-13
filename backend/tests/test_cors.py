import httpx
import pytest

from main import app


@pytest.mark.anyio
async def test_configured_frontend_origin_is_allowed() -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.options(
            "/api/products",
            headers={
                "Origin": "http://testserver",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "http://testserver"
    )


@pytest.mark.anyio
async def test_unknown_frontend_origin_is_rejected() -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.options(
            "/api/products",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers