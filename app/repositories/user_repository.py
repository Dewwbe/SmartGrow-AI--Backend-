from app.models.user import UserInDB
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserInDB]):
    collection_name = "users"
    model = UserInDB

    async def get_by_email(self, email: str) -> UserInDB | None:
        return await self.find_one({"email": email.lower()})
