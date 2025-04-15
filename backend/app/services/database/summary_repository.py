"""
Repository for managing email summaries in MongoDB.
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

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
        return self._model_class(**doc) if doc else None
    
    async def find_by_user_id(self, user_id: str) -> List[SummarySchema]:
        """
        Find summaries by user ID.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List[SummarySchema]: List of summaries
        """
        docs = await self.find_many({"user_id": user_id})
        return [self._model_class(**doc) for doc in docs]

    async def insert_one(self, summary: SummarySchema) -> str:
        """
        Insert a single summary.
        
        Args:
            summary: Summary to insert
            
        Returns:
            str: ID of the inserted summary
        """
        return await super().insert_one(summary.model_dump())

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