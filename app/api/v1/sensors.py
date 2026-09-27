"""
Two audiences hit this router: ESP32 devices push readings in via a device
API key (no user JWT -- the hardware can't do an OAuth login flow), and the
Flutter app / dashboard reads them back out via normal JWT auth.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_sensor_service, verify_device_api_key
from app.models.sensor_reading import SensorReadingCreate, SensorReadingPublic
from app.models.user import UserInDB
from app.services.sensor_service import SensorService

router = APIRouter(prefix="/sensors", tags=["Sensor Readings"])


@router.post(
    "/ingest",
    response_model=SensorReadingPublic,
    status_code=201,
    dependencies=[Depends(verify_device_api_key)],
)
async def ingest_reading(
    payload: SensorReadingCreate,
    sensor_service: Annotated[SensorService, Depends(get_sensor_service)],
):
    """Endpoint the ESP32 firmware POSTs to, authenticated via X-Device-Key header."""
    reading = await sensor_service.ingest_reading(payload)
    return SensorReadingPublic(**reading.model_dump())


@router.get("/trays/{tray_id}", response_model=list[SensorReadingPublic])
async def list_readings(
    tray_id: str,
    sensor_service: Annotated[SensorService, Depends(get_sensor_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    readings = await sensor_service.list_for_tray(tray_id, skip=skip, limit=limit)
    return [SensorReadingPublic(**r.model_dump()) for r in readings]


@router.get("/trays/{tray_id}/latest", response_model=SensorReadingPublic | None)
async def latest_reading(
    tray_id: str,
    sensor_service: Annotated[SensorService, Depends(get_sensor_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    reading = await sensor_service.latest_for_tray(tray_id)
    return SensorReadingPublic(**reading.model_dump()) if reading else None
