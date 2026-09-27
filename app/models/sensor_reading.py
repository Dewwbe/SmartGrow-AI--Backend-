"""
Raw telemetry ingested from an ESP32 per tray: one document per reading cycle.
This is intentionally flat and un-opinionated -- feature engineering for the
ML layer happens downstream, not at ingestion time.
"""

from pydantic import BaseModel, Field

from app.models.common import MongoBaseModel, PyObjectId, utcnow


class SensorReadingCreate(BaseModel):
    tray_id: str
    temperature_c: float
    relative_humidity_pct: float = Field(ge=0, le=100)
    substrate_moisture_pct: float = Field(ge=0, le=100)
    light_lux: float = Field(ge=0)
    hours_since_last_irrigation: float | None = None
    image_ref: str | None = None


class SensorReadingInDB(MongoBaseModel):
    tray_id: PyObjectId
    temperature_c: float
    relative_humidity_pct: float
    substrate_moisture_pct: float
    light_lux: float
    hours_since_last_irrigation: float | None = None
    image_ref: str | None = None
    recorded_at: str = Field(default_factory=lambda: utcnow().isoformat())


class SensorReadingPublic(BaseModel):
    id: PyObjectId
    tray_id: PyObjectId
    temperature_c: float
    relative_humidity_pct: float
    substrate_moisture_pct: float
    light_lux: float
    hours_since_last_irrigation: float | None
    image_ref: str | None
    recorded_at: str
