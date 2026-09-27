import pytest


@pytest.mark.asyncio
async def test_create_and_get_tray(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/trays",
        json={"tray_code": "SG-2026-001", "crop_type": "radish microgreen", "substrate": "cocopeat"},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    tray = create_resp.json()
    assert tray["tray_code"] == "SG-2026-001"

    get_resp = await client.get(f"/api/v1/trays/{tray['id']}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == tray["id"]


@pytest.mark.asyncio
async def test_duplicate_tray_code_rejected(client, auth_headers):
    payload = {"tray_code": "SG-2026-002", "crop_type": "pea shoots", "substrate": "cocopeat"}
    first = await client.post("/api/v1/trays", json=payload, headers=auth_headers)
    second = await client.post("/api/v1/trays", json=payload, headers=auth_headers)
    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_update_and_delete_tray(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/trays",
        json={"tray_code": "SG-2026-003", "crop_type": "sunflower", "substrate": "cocopeat"},
        headers=auth_headers,
    )
    tray_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/trays/{tray_id}", json={"status": "harvested", "harvest_weight_g": 245.5}, headers=auth_headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "harvested"

    delete_resp = await client.delete(f"/api/v1/trays/{tray_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/trays/{tray_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_list_trays_requires_auth(client):
    resp = await client.get("/api/v1/trays")
    assert resp.status_code == 401
