"""AI prediction outputs, kept separate from raw sensor data so re-training
never touches historical ground truth."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import MongoBaseModel, PyObjectId, utcnow


class PredictionRequest(BaseModel):
    tray_id: str
    temperature_c: float
    relative_humidity_pct: float
    substrate_moisture_pct: float
    light_lux: float
    crop_age_days: int = Field(ge=0)
    hours_since_last_irrigation: float = Field(ge=0)


class PredictionResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    predicted_moisture_pct: float
    irrigation_recommended: bool
    recommended_volume_ml: float
    fungal_risk: str
    model_version: str


class PredictionInDB(MongoBaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, protected_namespaces=())

    tray_id: PyObjectId
    input_features: dict
    predicted_moisture_pct: float
    irrigation_recommended: bool
    recommended_volume_ml: float
    fungal_risk: str
    model_version: str
    created_at: str = Field(default_factory=lambda: utcnow().isoformat())
