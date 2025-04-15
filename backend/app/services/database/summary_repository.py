"""
Repository for managing email summaries in MongoDB.
"""

from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.models import SummarySchema
from app.services.database.base_repository import BaseRepository

class SummaryRepository(BaseRepository):
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
        super().__init__(collection)
    
    async def find_by_email_id(self, email_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a summary by email ID and user ID.
        
        Args:
            email_id: ID of the email
            user_id: ID of the user
            
        Returns:
            Optional[Dict[str, Any]]: Summary if found, None otherwise
        """
        return await self.find_one({"email_id": email_id, "user_id": user_id})
    
    async def find_by_user_id(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find summaries by user ID.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of summaries to return
            
        Returns:
            List[Dict[str, Any]]: List of summaries
        """
        return await self.find_many({"user_id": user_id}, limit=limit)
    
    async def update_by_email_id(self, email_id: str, user_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a summary by email ID and user ID.
        
        Args:
            email_id: ID of the email
            user_id: ID of the user
            update_data: Data to update
            
        Returns:
            bool: True if update successful
        """
        result = await self._collection.update_one(
            {"email_id": email_id, "user_id": user_id},
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