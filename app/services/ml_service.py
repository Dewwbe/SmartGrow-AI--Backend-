"""Thin service layer between the API and the loaded ML model, so predictions
are always persisted alongside the inputs that produced them."""
from app.core.exceptions import NotFoundError
from app.ml.irrigation_model import irrigation_model
from app.models.prediction import PredictionInDB, PredictionRequest
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.tray_repository import TrayRepository


class MLService:
    def __init__(self, prediction_repo: PredictionRepository, tray_repo: TrayRepository):
        self.prediction_repo = prediction_repo
        self.tray_repo = tray_repo

    async def predict(self, payload: PredictionRequest) -> PredictionInDB:
        tray = await self.tray_repo.get_by_id(payload.tray_id)
        if not tray:
            raise NotFoundError("Tray", payload.tray_id)

        features = payload.model_dump(exclude={"tray_id"})
        result = irrigation_model.predict(features)

        document = {
            "tray_id": payload.tray_id,
            "input_features": features,
            **result,
        }
        return await self.prediction_repo.create(document)

    async def list_for_tray(self, tray_id: str, skip: int = 0, limit: int = 100):
        return await self.prediction_repo.list_for_tray(tray_id, skip=skip, limit=limit)
