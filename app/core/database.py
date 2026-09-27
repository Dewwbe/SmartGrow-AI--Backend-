"""
Single shared Motor (async MongoDB) client for the whole app.
Collections are exposed as simple properties so repositories don't each
re-derive collection names.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


class MongoDatabase:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

    def connect(self) -> None:
        self.client = AsyncIOMotorClient(settings.mongo_uri)
        self.db = self.client[settings.mongo_db_name]

    def close(self) -> None:
        if self.client:
            self.client.close()

    def get_db(self) -> AsyncIOMotorDatabase:
        if self.db is None:
            self.connect()
        return self.db


mongo = MongoDatabase()


def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency: yields the active Mongo database handle."""
    return mongo.get_db()
