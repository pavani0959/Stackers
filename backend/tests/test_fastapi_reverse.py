"""
Integration smoke test for the Reverse Shopping FastAPI endpoint.

The endpoint loads Fashion DNA and preferences from the
server-owned test database. The client sends only the prompt.
"""

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_reverse_fastapi():
    response = client.post(
        "/api/recommend/reverse",
        json={
            "prompt": (
                "Interview tomorrow under 2k"
            ),
        },
    )

    assert (
        response.status_code
        == 200
    ), response.text

    data = response.json()

    assert "outfits" in data
    assert "parsed_intent" in data

    assert (
        data["parsed_intent"][
            "occasion"
        ]
        == "interview"
    )

    assert (
        data["parsed_intent"][
            "budget_total"
        ]
        == 2000
    )
