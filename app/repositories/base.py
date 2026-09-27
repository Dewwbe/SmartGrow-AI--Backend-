"""
Generic async repository wrapping a single Mongo collection.

Concrete repositories subclass this and add domain-specific queries; the
common create/get/list/update/delete plumbing lives here exactly once.
"""
from typing import Any, Generic, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    collection_name: str
    model: type[ModelT]

    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection: AsyncIOMotorCollection = db[self.collection_name]

    @staticmethod
    def _to_object_id(id_str: str) -> ObjectId | None:
        return ObjectId(id_str) if ObjectId.is_valid(id_str) else None

    async def create(self, document: dict[str, Any]) -> ModelT:
        result = await self._collection.insert_one(document)
        created = await self._collection.find_one({"_id": result.inserted_id})
        return self.model(**created)

    async def get_by_id(self, id_str: str) -> ModelT | None:
        oid = self._to_object_id(id_str)
        if oid is None:
            return None
        doc = await self._collection.find_one({"_id": oid})
        return self.model(**doc) if doc else None

    async def find_one(self, query: dict[str, Any]) -> ModelT | None:
        doc = await self._collection.find_one(query)
        return self.model(**doc) if doc else None

    async def list(self, query: dict[str, Any] | None = None, skip: int = 0, limit: int = 50) -> list[ModelT]:
        cursor = self._collection.find(query or {}).sort("_id", -1).skip(skip).limit(limit)
        return [self.model(**doc) async for doc in cursor]

    async def update(self, id_str: str, updates: dict[str, Any]) -> ModelT | None:
        oid = self._to_object_id(id_str)
        if oid is None or not updates:
            return await self.get_by_id(id_str)
        await self._collection.update_one({"_id": oid}, {"$set": updates})
        return await self.get_by_id(id_str)

    async def delete(self, id_str: str) -> bool:
        oid = self._to_object_id(id_str)
        if oid is None:
            return False
        result = await self._collection.delete_one({"_id": oid})
        return result.deleted_count == 1

    async def count(self, query: dict[str, Any] | None = None) -> int:
        return await self._collection.count_documents(query or {})
