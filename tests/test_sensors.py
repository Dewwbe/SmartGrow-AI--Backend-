import pytest

from app.core.config import settings


@pytest.mark.asyncio
async def test_device_can_ingest_reading(client, auth_headers):
    tray_resp = await client.post(
        "/api/v1/trays",
        json={"tray_code": "SG-2026-010", "crop_type": "radish", "substrate": "cocopeat"},
        headers=auth_headers,
    )
    tray_id = tray_resp.json()["id"]

    ingest_resp = await client.post(
        "/api/v1/sensors/ingest",
        json={
            "tray_id": tray_id,
            "temperature_c": 27.5,
            "relative_humidity_pct": 78,
            "substrate_moisture_pct": 55,
            "light_lux": 4200,
            "hours_since_last_irrigation": 3,
        },
        headers={"X-Device-Key": settings.device_api_key},
    )
    assert ingest_resp.status_code == 201
    assert ingest_resp.json()["tray_id"] == tray_id


@pytest.mark.asyncio
async def test_ingest_rejected_without_device_key(client, auth_headers):
    tray_resp = await client.post(
        "/api/v1/trays",
        json={"tray_code": "SG-2026-011", "crop_type": "radish", "substrate": "cocopeat"},
        headers=auth_headers,
    )
    tray_id = tray_resp.json()["id"]

    resp = await client.post(
        "/api/v1/sensors/ingest",
        json={
            "tray_id": tray_id,
            "temperature_c": 27.5,
            "relative_humidity_pct": 78,
            "substrate_moisture_pct": 55,
            "light_lux": 4200,
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_readings_for_tray(client, auth_headers):
    tray_resp = await client.post(
        "/api/v1/trays",
        json={"tray_code": "SG-2026-012", "crop_type": "radish", "substrate": "cocopeat"},
        headers=auth_headers,
    )
    tray_id = tray_resp.json()["id"]

    await client.post(
        "/api/v1/sensors/ingest",
        json={
            "tray_id": tray_id, "temperature_c": 26, "relative_humidity_pct": 70,
            "substrate_moisture_pct": 60, "light_lux": 4000,
        },
        headers={"X-Device-Key": settings.device_api_key},
    )

    list_resp = await client.get(f"/api/v1/sensors/trays/{tray_id}", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
