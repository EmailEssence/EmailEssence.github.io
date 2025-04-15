"""
Base repository class for common database operations.
"""

from typing import Dict, Any, Optional, List, Generic, TypeVar, Type
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
import logging
from pydantic import BaseModel

from app.services.database.connection import instance

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """
    Base repository class for MongoDB operations.
    
    This class provides common database operations that can be inherited
    by specific repository implementations.
    """
    
    def __init__(self, collection: AsyncIOMotorCollection, model_class: Type[T]):
        """
        Initialize the repository with a MongoDB collection.
        
        Args:
            collection: MongoDB collection instance
            model_class: Pydantic model class for type safety
        """
        self._collection = collection
        self._model_class = model_class

    def _get_collection(self) -> AsyncIOMotorCollection:
        """
        Get the MongoDB collection instance.
        
        Returns:
            AsyncIOMotorCollection: MongoDB collection instance
        """
        if self._collection is None:
            self._collection = instance.db[self.collection_name]
        return self._collection

    async def create_index(self, field: str, unique: bool = False, **kwargs) -> None:
        """
        Create an index on the specified field.
        
        Args:
            field: Field to create index on
            unique: Whether the index should enforce uniqueness
            **kwargs: Additional index options
        """
        try:
            await self._collection.create_index(field, unique=unique, **kwargs)
            logger.info(f"Created index on {field} (unique={unique})")
        except Exception as e:
            logger.error(f"Failed to create index on {field}: {e}")
            raise

    async def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        """
        Find a single document matching the query.
        
        Args:
            query: MongoDB query filter
            
        Returns:
            Optional[T]: Document if found, None otherwise
        """
        collection = self._get_collection()
        doc = await collection.find_one(query)
        return self._model_class(**doc) if doc else None

    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Find a document by its ID.
        
        Args:
            id: Document ID
            
        Returns:
            Optional[Dict[str, Any]]: Document if found, None otherwise
        """
        if not ObjectId.is_valid(id):
            return None
        return await self.find_one({"_id": ObjectId(id)})

    async def find_many(self, query: Dict[str, Any], limit: int = 100, skip: int = 0, sort: List[tuple] = None) -> List[Dict[str, Any]]:
        """
        Find multiple documents matching the query with pagination support.
        
        Args:
            query: MongoDB query filter
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            sort: List of (field, direction) tuples for sorting
            
        Returns:
            List[Dict[str, Any]]: List of matching documents
        """
        collection = self._get_collection()
        cursor = collection.find(query)
        
        if sort:
            cursor = cursor.sort(sort)
            
        cursor = cursor.skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def insert_one(self, document: Dict[str, Any]) -> str:
        """
        Insert a single document.
        
        Args:
            document: Document to insert
            
        Returns:
            str: ID of the inserted document
        """
        collection = self._get_collection()
        result = await collection.insert_one(document)
        return str(result.inserted_id)

    async def update_one(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a single document by ID.
        
        Args:
            document_id: ID of the document to update
            update_data: Data to update
            
        Returns:
            bool: True if update successful
        """
        if not ObjectId.is_valid(document_id):
            return False
        collection = self._get_collection()
        result = await collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_one(self, document_id: str) -> bool:
        """
        Delete a single document by ID.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            bool: True if deletion successful
        """
        if not ObjectId.is_valid(document_id):
            return False
        collection = self._get_collection()
        result = await collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0

    async def count_documents(self, query: Dict[str, Any]) -> int:
        """
        Count the number of documents matching the query.
        
        Args:
            query: MongoDB query filter
            
        Returns:
            int: Number of matching documents
        """
        collection = self._get_collection()
        return await collection.count_documents(query) 