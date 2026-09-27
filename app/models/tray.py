"""A cultivation tray: the unit everything else (readings, irrigation, predictions) hangs off."""
from typing import Literal

from pydantic import BaseModel, Field

from app.models.common import MongoBaseModel, PyObjectId, utcnow

TrayStatus = Literal["active", "harvested", "empty", "failed"]


class TrayCreate(BaseModel):
    tray_code: str = Field(min_length=1, max_length=40, description="e.g. SG-2026-001")
    crop_type: str = Field(default="microgreen")
    substrate: str = Field(default="cocopeat")
    sown_at: str | None = None
    notes: str | None = None


class TrayUpdate(BaseModel):
    crop_type: str | None = None
    status: TrayStatus | None = None
    notes: str | None = None
    harvested_at: str | None = None
    harvest_weight_g: float | None = None


class TrayInDB(MongoBaseModel):
    tray_code: str
    crop_type: str
    substrate: str
    status: TrayStatus = "active"
    sown_at: str | None = None
    harvested_at: str | None = None
    harvest_weight_g: float | None = None
    notes: str | None = None
    owner_id: PyObjectId
    created_at: str = Field(default_factory=lambda: utcnow().isoformat())


class TrayPublic(BaseModel):
    id: PyObjectId
    tray_code: str
    crop_type: str
    substrate: str
    status: TrayStatus
    sown_at: str | None
    harvested_at: str | None
    harvest_weight_g: float | None
    notes: str | None
