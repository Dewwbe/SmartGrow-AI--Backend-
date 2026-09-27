from app.core.exceptions import DuplicateError, NotFoundError
from app.models.tray import TrayCreate, TrayInDB, TrayUpdate
from app.repositories.tray_repository import TrayRepository


class TrayService:
    def __init__(self, tray_repo: TrayRepository):
        self.tray_repo = tray_repo

    async def create_tray(self, payload: TrayCreate, owner_id: str) -> TrayInDB:
        existing = await self.tray_repo.get_by_code(payload.tray_code)
        if existing:
            raise DuplicateError("Tray", "tray_code", payload.tray_code)
        document = payload.model_dump()
        document["owner_id"] = owner_id
        return await self.tray_repo.create(document)

    async def get_tray(self, tray_id: str) -> TrayInDB:
        tray = await self.tray_repo.get_by_id(tray_id)
        if not tray:
            raise NotFoundError("Tray", tray_id)
        return tray

    async def list_trays(self, owner_id: str, skip: int = 0, limit: int = 50) -> list[TrayInDB]:
        return await self.tray_repo.list_for_owner(owner_id, skip=skip, limit=limit)

    async def update_tray(self, tray_id: str, payload: TrayUpdate) -> TrayInDB:
        await self.get_tray(tray_id)  # 404s if missing
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        return await self.tray_repo.update(tray_id, updates)

    async def delete_tray(self, tray_id: str) -> None:
        await self.get_tray(tray_id)
        await self.tray_repo.delete(tray_id)
