"""
Refresh-token denylist: on logout we store the token's jti here so a stolen
or client-cached refresh token can't be replayed after the user logs out,
even though it hasn't technically expired yet.
"""
from app.core.database import get_database


class TokenDenylistRepository:
    collection_name = "revoked_tokens"

    def __init__(self, db=None):
        self._collection = (db or get_database())[self.collection_name]

    async def revoke(self, jti: str) -> None:
        await self._collection.update_one({"jti": jti}, {"$set": {"jti": jti}}, upsert=True)

    async def is_revoked(self, jti: str) -> bool:
        return await self._collection.find_one({"jti": jti}) is not None
