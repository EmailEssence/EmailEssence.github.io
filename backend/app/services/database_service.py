from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId

class DatabaseService:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one(query)

    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": ObjectId(id)})

    async def find_many(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        return await self.collection.find(query).to_list(length=limit)

    async def insert_one(self, data: Dict[str, Any]) -> Any:
        return await self.collection.insert_one(data)

    async def update_one(self, query: Dict[str, Any], data: Dict[str, Any], upsert: bool = False) -> Any:
        return await self.collection.update_one(query, {"$set": data}, upsert=upsert)

    async def delete_one(self, query: Dict[str, Any]) -> Any:
        return await self.collection.delete_one(query)