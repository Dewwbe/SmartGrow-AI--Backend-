import pytest


@pytest.mark.asyncio
async def test_prediction_uses_heuristic_fallback_when_no_model_trained(client, auth_headers):
    tray_resp = await client.post(
        "/api/v1/trays",
        json={"tray_code": "SG-2026-020", "crop_type": "radish", "substrate": "cocopeat"},
        headers=auth_headers,
    )
    tray_id = tray_resp.json()["id"]

    resp = await client.post(
        "/api/v1/predictions",
        json={
            "tray_id": tray_id,
            "temperature_c": 30,
            "relative_humidity_pct": 85,
            "substrate_moisture_pct": 45,
            "light_lux": 5000,
            "crop_age_days": 5,
            "hours_since_last_irrigation": 6,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "predicted_moisture_pct" in body
    assert body["model_version"].startswith("heuristic")
    assert body["fungal_risk"] in {"low", "elevated", "high"}


@pytest.mark.asyncio
async def test_prediction_for_missing_tray_returns_404(client, auth_headers):
    resp = await client.post(
        "/api/v1/predictions",
        json={
            "tray_id": "64b7f9f9f9f9f9f9f9f9f9f9",
            "temperature_c": 25, "relative_humidity_pct": 60,
            "substrate_moisture_pct": 50, "light_lux": 3000,
            "crop_age_days": 3, "hours_since_last_irrigation": 4,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404
