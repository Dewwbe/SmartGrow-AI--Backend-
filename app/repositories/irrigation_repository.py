from app.models.irrigation import IrrigationEventInDB
from app.repositories.base import BaseRepository


class IrrigationRepository(BaseRepository[IrrigationEventInDB]):
    collection_name = "irrigation_events"
    model = IrrigationEventInDB

    async def list_for_tray(self, tray_id: str, skip: int = 0, limit: int = 100) -> list[IrrigationEventInDB]:
        return await self.list({"tray_id": tray_id}, skip=skip, limit=limit)
