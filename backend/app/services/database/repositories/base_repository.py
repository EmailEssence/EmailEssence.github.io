"""
Base repository class for common database operations.
"""

from typing import Dict, Any, Optional, List, Generic, TypeVar, Type
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from app.services.database.connection import instance

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
        self.collection = collection
        self.model_class = model_class

    def _get_collection(self) -> AsyncIOMotorCollection:
        """
        Get the MongoDB collection instance.
        
        Returns:
            AsyncIOMotorCollection: MongoDB collection instance
        """
        if self.collection is None:
            self.collection = instance.db[self.collection_name]
        return self.collection

    def _to_model(self, doc: Optional[Dict[str, Any]]) -> Optional[T]:
        """
        Convert a MongoDB document to a model instance.
        
        Args:
            doc: MongoDB document
            
        Returns:
            Optional[T]: Model instance if document exists, None otherwise
        """
        if doc is None:
            return None
        try:
            # If doc is already a model instance, return it directly
            if isinstance(doc, self.model_class):
                return doc
            # Otherwise convert dict to model
            return self.model_class(**doc)
        except Exception as e:
            raise

    def _to_document(self, model: T) -> Dict[str, Any]:
        """
        Convert a model instance to a MongoDB document.
        
        Args:
            model: Model instance
            
        Returns:
            Dict[str, Any]: MongoDB document
        """
        try:
            # If model is already a dict, return it directly
            if isinstance(model, dict):
                return model
            # Otherwise convert model to dict
            return model.model_dump()
        except Exception as e:
            raise

    async def create_index(self, field: str, unique: bool = False, **kwargs) -> None:
        """
        Create an index on the specified field.
        
        Args:
            field: Field to create index on
            unique: Whether the index should enforce uniqueness
            **kwargs: Additional index options
        """
        try:
            await self._get_collection().create_index(field, unique=unique, **kwargs)
        except Exception as e:
            raise

    async def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        """
        Find a single document matching the query.
        
        Args:
            query: MongoDB query filter
            
        Returns:
            Optional[T]: Document if found, None otherwise
        """
        try:
            doc = await self._get_collection().find_one(query)
            return self._to_model(doc)
        except Exception as e:
            raise

    async def find_by_id(self, id: str) -> Optional[T]:
        """
        Find a document by its ID.
        
        Args:
            id: Document ID
            
        Returns:
            Optional[T]: Document if found, None otherwise
        """
        if not ObjectId.is_valid(id):
            return None
        return await self.find_one({"_id": ObjectId(id)})

    async def find_many(
        self, 
        query: Dict[str, Any], 
        limit: int = 100, 
        skip: int = 0, 
        sort: List[tuple] = None
    ) -> List[T]:
        """
        Find multiple documents matching the query with pagination support.
        
        Args:
            query: MongoDB query filter
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            sort: List of (field, direction) tuples for sorting
            
        Returns:
            List[T]: List of matching documents
        """
        try:
            cursor = self._get_collection().find(query)
            
            if sort:
                cursor = cursor.sort(sort)
                
            cursor = cursor.skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [self._to_model(doc) for doc in docs]
        except Exception as e:
            raise

    async def insert_one(self, model: T) -> str:
        """
        Insert a single document.
        
        Args:
            model: Model instance to insert
            
        Returns:
            str: ID of the inserted document
        """
        try:
            document = self._to_document(model)
            result = await self._get_collection().insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            raise

    async def insert_many(self, models: List[T]) -> List[str]:
        """
        Insert multiple documents.
        
        Args:
            models: List of model instances to insert
            
        Returns:
            List[str]: IDs of the inserted documents
        """
        if not models:
            return []
            
        try:
            documents = [self._to_document(model) for model in models]
            result = await self._get_collection().insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            raise

    async def bulk_write(self, operations: List[Dict[str, Any]]) -> Any:
        """
        Execute multiple update operations in bulk.
        
        Args:
            operations: List of operations, each containing:
                - filter: Query to select documents
                - update: Update to apply
                - upsert: Whether to create documents if they don't exist
            
        Returns:
            Any: Result of the bulk write operation
        """
        if not operations:
            return None
            
        try:
            # Convert operations to PyMongo bulk operations
            bulk_ops = []
            for op in operations:
                bulk_ops.append(
                    UpdateOne(
                        filter=op['filter'],
                        update={'$set': op['update']},
                        upsert=op.get('upsert', False)
                    )
                )
                
            # Execute bulk write
            result = await self._get_collection().bulk_write(bulk_ops)
            return result
        except Exception as e:
            raise

    async def update_one(
        self, 
        query: Dict[str, Any], 
        update_data: Dict[str, Any],
        upsert: bool = False
    ) -> bool:
        """
        Update a single document matching the query.
        
        Args:
            query: MongoDB query filter
            update_data: Data to update
            upsert: If True, create a new document if no match is found
            
        Returns:
            bool: True if update successful
        """
        try:
            result = await self._get_collection().update_one(
                query,
                {"$set": update_data},
                upsert=upsert
            )
            return result.modified_count > 0 or (upsert and result.upserted_id is not None)
        except Exception as e:
            raise

    async def delete_one(self, query: Dict[str, Any]) -> bool:
        """
        Delete a single document matching the query.
        
        Args:
            query: MongoDB query filter
            
        Returns:
            bool: True if deletion successful
        """
        try:
            result = await self._get_collection().delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            raise

    async def count_documents(self, query: Dict[str, Any]) -> int:
        """
        Count the number of documents matching the query.
        
        Args:
            query: MongoDB query filter
            
        Returns:
            int: Number of matching documents
        """
        try:
            return await self._get_collection().count_documents(query)
        except Exception as e:
            raise

    async def upsert_one(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> str:
        """
        Update a document if it exists, otherwise insert it.
        
        Args:
            query: MongoDB query filter to find the document
            update_data: Data to update/insert
            
        Returns:
            str: ID of the document (existing or newly inserted)
        """
        try:
            result = await self._get_collection().update_one(
                query,
                {"$set": update_data},
                upsert=True
            )
            if result.upserted_id:
                return str(result.upserted_id)
            # If no upsert happened, find the existing document
            doc = await self.find_one(query)
            if doc:
                # Try to get _id first, then try the query key
                if hasattr(doc, '_id'):
                    return str(doc._id)
                # Get the first key from the query as the identifier
                identifier_key = next(iter(query.keys()))
                return str(getattr(doc, identifier_key))
            return None
        except Exception as e:
            raise

    async def find_by_google_id(self, google_id: str) -> Optional[T]:
        """
        Find a document by Google ID.
        
        Args:
            google_id: Google ID to search for
            
        Returns:
            Optional[T]: Document if found, None otherwise
        """
        return await self.find_one({"google_id": google_id})

    async def update_by_google_id(self, google_id: str, update_data: Dict[str, Any], upsert: bool = False) -> bool:
        """
        Update a document by Google ID.
        
        Args:
            google_id: Google ID of the document to update
            update_data: Data to update
            upsert: If True, create a new document if no match is found
            
        Returns:
            bool: True if update successful
        """
        return await self.update_one({"google_id": google_id}, update_data, upsert=upsert)

    async def delete_by_google_id(self, google_id: str) -> bool:
        """
        Delete a document by Google ID.
        
        Args:
            google_id: Google ID of the document to delete
            
        Returns:
            bool: True if deletion successful
        """
        return await self.delete_one({"google_id": google_id}) 