import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "password": "password123", "full_name": "A B"},
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["email"] == "a@example.com"

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.com", "password": "password123"},
    )
    assert login_resp.status_code == 200
    body = login_resp.json()
    assert "access_token" in body and "refresh_token" in body


@pytest.mark.asyncio
async def test_duplicate_registration_rejected(client):
    payload = {"email": "dup@example.com", "password": "password123", "full_name": "Dup"}
    first = await client.post("/api/v1/auth/register", json=payload)
    second = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password_rejected(client, registered_user):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": "wrong-password"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_token(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_token(client, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "grower@example.com"


@pytest.mark.asyncio
async def test_refresh_and_logout(client, registered_user):
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    refresh_token = login_resp.json()["refresh_token"]

    refresh_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()

    logout_resp = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 204

    # Refresh token should now be rejected -- it was revoked on logout.
    reused_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert reused_resp.status_code == 401
