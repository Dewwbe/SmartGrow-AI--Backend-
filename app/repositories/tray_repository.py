from app.models.tray import TrayInDB
from app.repositories.base import BaseRepository


class TrayRepository(BaseRepository[TrayInDB]):
    collection_name = "trays"
    model = TrayInDB

    async def get_by_code(self, tray_code: str) -> TrayInDB | None:
        return await self.find_one({"tray_code": tray_code})

    async def list_for_owner(self, owner_id: str, skip: int = 0, limit: int = 50) -> list[TrayInDB]:
        return await self.list({"owner_id": owner_id}, skip=skip, limit=limit)
