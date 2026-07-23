"""Tests for the authentication routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# ── Signup tests ────────────────────────────────────────


def test_signup_creates_user_and_returns_token():
    response = client.post(
        "/api/auth/signup",
        json={
            "name": "Auth Test User",
            "email": "authtest@example.com",
            "password": "securePass123",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "authtest@example.com"
    assert data["user"]["name"] == "Auth Test User"
    assert data["user"]["onboarding_completed"] is False


def test_signup_duplicate_email_rejected():
    # First signup should succeed
    client.post(
        "/api/auth/signup",
        json={
            "name": "Dup User",
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )

    # Second signup with same email should fail
    response = client.post(
        "/api/auth/signup",
        json={
            "name": "Dup User 2",
            "email": "duplicate@example.com",
            "password": "password456",
        },
    )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_signup_short_password_rejected():
    response = client.post(
        "/api/auth/signup",
        json={
            "name": "Short Pass",
            "email": "shortpass@example.com",
            "password": "abc",
        },
    )

    assert response.status_code == 422


# ── Login tests ─────────────────────────────────────────


def test_login_with_valid_credentials():
    # Create user first
    client.post(
        "/api/auth/signup",
        json={
            "name": "Login User",
            "email": "loginuser@example.com",
            "password": "myPassword1",
        },
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "myPassword1",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "loginuser@example.com"


def test_login_with_wrong_password():
    # Create user first
    client.post(
        "/api/auth/signup",
        json={
            "name": "Wrong Pass",
            "email": "wrongpass@example.com",
            "password": "correctPassword",
        },
    )

    # Login with wrong password
    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "incorrectPassword",
        },
    )

    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


def test_login_with_nonexistent_email():
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nobody@nowhere.com",
            "password": "anything",
        },
    )

    assert response.status_code == 401


# ── /me endpoint tests ──────────────────────────────────


def test_me_with_valid_token():
    # Sign up to get a token
    signup_response = client.post(
        "/api/auth/signup",
        json={
            "name": "Me User",
            "email": "meuser@example.com",
            "password": "testPass99",
        },
    )

    token = signup_response.json()["token"]

    # Use token to call /me
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "meuser@example.com"


def test_me_without_token_rejected():
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_with_invalid_token_rejected():
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer totally.invalid.token"},
    )

    assert response.status_code == 401


# ── Protected route with JWT ────────────────────────────


def test_profile_route_works_with_jwt():
    """A signed-up user can access /api/profile using their JWT."""
    # Create user and onboard them
    signup_resp = client.post(
        "/api/auth/signup",
        json={
            "name": "Profile Auth User",
            "email": "profileauth@example.com",
            "password": "securePass1",
        },
    )

    token = signup_resp.json()["token"]

    # The profile endpoint should return data for this user
    response = client.get(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
    )

    # The user exists so profile should load (may be minimal)
    assert response.status_code == 200
    assert response.json()["user"]["name"] == "Profile Auth User"


def test_existing_demo_routes_still_work_without_token():
    """Existing routes still work without a token via demo_user fallback."""
    response = client.get("/api/profile")

    assert response.status_code == 200
    assert "user" in response.json()
