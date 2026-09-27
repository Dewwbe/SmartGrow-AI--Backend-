"""
Ingests readings pushed by ESP32 devices and serves them back out for the
dashboard / analytics / ML feature pipeline.
"""
from app.core.exceptions import NotFoundError
from app.models.sensor_reading import SensorReadingCreate, SensorReadingInDB
from app.repositories.sensor_repository import SensorRepository
from app.repositories.tray_repository import TrayRepository


class SensorService:
    def __init__(self, sensor_repo: SensorRepository, tray_repo: TrayRepository):
        self.sensor_repo = sensor_repo
        self.tray_repo = tray_repo

    async def ingest_reading(self, payload: SensorReadingCreate) -> SensorReadingInDB:
        tray = await self.tray_repo.get_by_id(payload.tray_id)
        if not tray:
            raise NotFoundError("Tray", payload.tray_id)
        return await self.sensor_repo.create(payload.model_dump())

    async def list_for_tray(self, tray_id: str, skip: int = 0, limit: int = 100) -> list[SensorReadingInDB]:
        return await self.sensor_repo.list_for_tray(tray_id, skip=skip, limit=limit)

    async def latest_for_tray(self, tray_id: str) -> SensorReadingInDB | None:
        return await self.sensor_repo.latest_for_tray(tray_id)
