from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_generated_request_id_is_returned():
    response = client.get(
        "/health",
    )

    assert response.status_code == 200

    request_id = response.headers.get(
        "X-Request-ID",
    )

    assert request_id
    assert len(request_id) <= 128


def test_supplied_request_id_is_preserved():
    response = client.get(
        "/health",
        headers={
            "X-Request-ID":
                "phase9-observability-test",
        },
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "X-Request-ID"
        ]
        == "phase9-observability-test"
    )
