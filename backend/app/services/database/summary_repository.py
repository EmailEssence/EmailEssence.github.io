"""
Repository for managing email summaries in MongoDB.
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime

from app.models.summary_models import SummarySchema
from app.services.database.base_repository import BaseRepository
from app.services.database.interfaces import ISummaryRepository

class SummaryRepository(BaseRepository[SummarySchema], ISummaryRepository):
    """
    Repository for managing email summaries in MongoDB.
    
    This class provides methods for storing, retrieving, and managing
    email summaries in the database.
    """
    
    def __init__(self, collection: AsyncIOMotorCollection):
        """
        Initialize the summary repository.
        
        Args:
            collection: MongoDB collection instance
        """
        super().__init__(collection, SummarySchema)
    
    async def find_by_email_id(self, email_id: str) -> Optional[SummarySchema]:
        """
        Find a summary by email ID.
        
        Args:
            email_id: ID of the email
            
        Returns:
            Optional[SummarySchema]: Summary if found, None otherwise
        """
        doc = await self.find_one({"email_id": email_id})
        if doc:
            # If doc is already a SummarySchema instance, return it directly
            if isinstance(doc, SummarySchema):
                return doc
            # Otherwise convert dict to SummarySchema
            return self._model_class(**doc)
        return None
    
    async def find_by_user_id(self, user_id: str) -> List[SummarySchema]:
        """
        Find summaries by user ID.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List[SummarySchema]: List of summaries
        """
        docs = await self.find_many({"user_id": user_id})
        return [self._model_class(**doc) if not isinstance(doc, SummarySchema) else doc for doc in docs]

    async def insert_one(self, summary: SummarySchema) -> str:
        """
        Insert a single summary.
        
        Args:
            summary: Summary to insert
            
        Returns:
            str: ID of the inserted summary
        """
        # If summary is already a SummarySchema instance, use it directly
        if isinstance(summary, SummarySchema):
            return await super().insert_one(summary)
        # Otherwise create a new SummarySchema instance
        return await super().insert_one(self._model_class(**summary))

    async def update_by_email_id(self, email_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a summary by email ID.
        
        Args:
            email_id: ID of the email
            update_data: Data to update
            
        Returns:
            bool: True if update successful
        """
        result = await self._collection.update_one(
            {"email_id": email_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_by_email_id(self, email_id: str, user_id: str) -> bool:
        """
        Delete a summary by email ID and user ID.
        
        Args:
            email_id: ID of the email
            user_id: ID of the user
            
        Returns:
            bool: True if deletion successful
        """
        result = await self._collection.delete_one({"email_id": email_id, "user_id": user_id})
        return result.deleted_count > 0

    async def find_many(
        self, 
        query: Dict[str, Any], 
        limit: int = 100, 
        skip: int = 0, 
        sort: List[tuple] = None
    ) -> List[SummarySchema]:
        """
        Find multiple summaries matching the query.
        
        Args:
            query: MongoDB query filter
            limit: Maximum number of summaries to return
            skip: Number of summaries to skip
            sort: List of (field, direction) tuples for sorting
            
        Returns:
            List[SummarySchema]: List of matching summaries
        """
        try:
            # Ensure datetime fields are properly handled
            if "generated_at" in query:
                if isinstance(query["generated_at"], dict):
                    for op, value in query["generated_at"].items():
                        if isinstance(value, datetime):
                            query["generated_at"][op] = value
            
            docs = await super().find_many(query, limit, skip, sort)
            return [self._to_model(doc) for doc in docs]
        except Exception as e:
            raise 