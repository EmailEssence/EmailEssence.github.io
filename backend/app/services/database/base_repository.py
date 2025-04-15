from typing import TypeVar, Generic, Dict, List, Optional, Any, Type
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorCollection
from app.services.database.mongodb_service import MongoDBService

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """
    Generic base repository class that provides common database operations
    with type safety and model conversion.
    
    Args:
        collection: MongoDB collection instance
        model_class: Pydantic model class for type conversion
    """
    def __init__(self, collection: AsyncIOMotorCollection, model_class: Type[T]):
        self.db_service = MongoDBService(collection)
        self.model_class = model_class
        
    def _to_model(self, data: Dict[str, Any]) -> Optional[T]:
        """Convert dictionary to model instance"""
        if data is None:
            return None
        return self.model_class(**data)
    
    def _to_dict(self, model: T) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        return model.dict(exclude_unset=True)
        
    async def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        """Find a single document matching the query"""
        data = await self.db_service.find_one(query)
        return self._to_model(data)
    
    async def find_by_id(self, id: str) -> Optional[T]:
        """Find a document by its ID"""
        data = await self.db_service.find_by_id(id)
        return self._to_model(data)
    
    async def find_many(self, query: Dict[str, Any], limit: int = 100) -> List[T]:
        """Find multiple documents matching the query"""
        data_list = await self.db_service.find_many(query, limit)
        return [self._to_model(data) for data in data_list]
    
    async def insert_one(self, model: T) -> Any:
        """Insert a single document"""
        data = self._to_dict(model)
        return await self.db_service.insert_one(data)
    
    async def update_one(self, query: Dict[str, Any], model: T, upsert: bool = False) -> Any:
        """Update a single document"""
        data = self._to_dict(model)
        return await self.db_service.update_one(query, data, upsert)
    
    async def delete_one(self, query: Dict[str, Any]) -> Any:
        """Delete a single document"""
        return await self.db_service.delete_one(query) 