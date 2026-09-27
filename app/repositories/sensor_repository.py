from app.models.sensor_reading import SensorReadingInDB
from app.repositories.base import BaseRepository


class SensorRepository(BaseRepository[SensorReadingInDB]):
    collection_name = "sensor_readings"
    model = SensorReadingInDB

    async def list_for_tray(self, tray_id: str, skip: int = 0, limit: int = 100) -> list[SensorReadingInDB]:
        return await self.list({"tray_id": tray_id}, skip=skip, limit=limit)

    async def latest_for_tray(self, tray_id: str) -> SensorReadingInDB | None:
        readings = await self.list({"tray_id": tray_id}, skip=0, limit=1)
        return readings[0] if readings else None
