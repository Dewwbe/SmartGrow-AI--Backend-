from app.models.prediction import PredictionInDB
from app.repositories.base import BaseRepository


class PredictionRepository(BaseRepository[PredictionInDB]):
    collection_name = "predictions"
    model = PredictionInDB

    async def list_for_tray(self, tray_id: str, skip: int = 0, limit: int = 100) -> list[PredictionInDB]:
        return await self.list({"tray_id": tray_id}, skip=skip, limit=limit)
