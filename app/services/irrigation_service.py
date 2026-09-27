from app.core.exceptions import NotFoundError
from app.models.irrigation import IrrigationEventCreate, IrrigationEventInDB
from app.repositories.irrigation_repository import IrrigationRepository
from app.repositories.tray_repository import TrayRepository


class IrrigationService:
    def __init__(self, irrigation_repo: IrrigationRepository, tray_repo: TrayRepository):
        self.irrigation_repo = irrigation_repo
        self.tray_repo = tray_repo

    async def record_event(self, payload: IrrigationEventCreate) -> IrrigationEventInDB:
        tray = await self.tray_repo.get_by_id(payload.tray_id)
        if not tray:
            raise NotFoundError("Tray", payload.tray_id)
        return await self.irrigation_repo.create(payload.model_dump())

    async def list_for_tray(self, tray_id: str, skip: int = 0, limit: int = 100) -> list[IrrigationEventInDB]:
        return await self.irrigation_repo.list_for_tray(tray_id, skip=skip, limit=limit)
