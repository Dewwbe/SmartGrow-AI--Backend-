"""
Wraps the trained irrigation/moisture model.

If no trained artifact exists yet (fresh clone, first hackathon day before
you've collected a crop cycle of data), it falls back to a transparent
heuristic so the API never breaks -- it just tells you it's using the
fallback via `model_version`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.core.config import settings

FEATURE_ORDER = [
    "temperature_c",
    "relative_humidity_pct",
    "substrate_moisture_pct",
    "light_lux",
    "crop_age_days",
    "hours_since_last_irrigation",
]


class IrrigationModel:
    def __init__(self, model_path: str | None = None):
        self.model_path = Path(model_path or settings.model_path)
        self._model = self._load()

    def _load(self):
        if self.model_path.exists():
            return joblib.load(self.model_path)
        return None

    @property
    def version(self) -> str:
        return f"trained:{self.model_path.name}" if self._model is not None else "heuristic:v0"

    def _heuristic_predict(self, features: dict[str, Any]) -> float:
        """
        Simple, explainable fallback: moisture decays with time since
        irrigation and rises with temperature/humidity-driven evaporation.
        Tuned to be roughly plausible for cocopeat, not scientifically fit.
        """
        moisture = features["substrate_moisture_pct"]
        hours = features["hours_since_last_irrigation"]
        temp_factor = max(features["temperature_c"] - 24, 0) * 0.4
        humidity_relief = max(features["relative_humidity_pct"] - 60, 0) * 0.1
        decay = hours * (1.2 + temp_factor - humidity_relief)
        return float(max(moisture - decay, 0))

    def predict_moisture(self, features: dict[str, Any]) -> float:
        if self._model is None:
            return self._heuristic_predict(features)
        ordered = np.array([[features[key] for key in FEATURE_ORDER]])
        prediction = self._model.predict(ordered)[0]
        return float(prediction)

    def predict(self, features: dict[str, Any]) -> dict[str, Any]:
        predicted_moisture = self.predict_moisture(features)
        irrigation_recommended = predicted_moisture < 40.0
        recommended_volume = 150.0 if irrigation_recommended else 0.0

        fungal_risk = "low"
        if features["relative_humidity_pct"] > 80 and features["substrate_moisture_pct"] > 70:
            fungal_risk = "elevated"
        if features["relative_humidity_pct"] > 90 and features["substrate_moisture_pct"] > 80:
            fungal_risk = "high"

        return {
            "predicted_moisture_pct": round(predicted_moisture, 2),
            "irrigation_recommended": irrigation_recommended,
            "recommended_volume_ml": recommended_volume,
            "fungal_risk": fungal_risk,
            "model_version": self.version,
        }


irrigation_model = IrrigationModel()
