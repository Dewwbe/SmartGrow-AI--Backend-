"""Irrigation events: both AI-recommended and the actual outcome recorded afterwards."""

from pydantic import BaseModel, Field

from app.models.common import MongoBaseModel, PyObjectId, utcnow


class IrrigationEventCreate(BaseModel):
    tray_id: str
    volume_ml: float = Field(ge=0)
    triggered_by: str = Field(default="manual", description="manual | ai | schedule")


class IrrigationEventInDB(MongoBaseModel):
    tray_id: PyObjectId
    volume_ml: float
    triggered_by: str
    predicted_moisture_pct: float | None = None
    actual_moisture_pct_after: float | None = None
    prediction_error: float | None = None
    created_at: str = Field(default_factory=lambda: utcnow().isoformat())


class IrrigationEventPublic(BaseModel):
    id: PyObjectId
    tray_id: PyObjectId
    volume_ml: float
    triggered_by: str
    predicted_moisture_pct: float | None
    actual_moisture_pct_after: float | None
    prediction_error: float | None
    created_at: str
