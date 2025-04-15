"""
Repository for managing emails in MongoDB.
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection

from app.models import EmailSchema
from app.services.database.base_repository import BaseRepository

class EmailRepository(BaseRepository):
    """
    Repository for managing emails in MongoDB.
    
    This class provides methods for storing, retrieving, and managing
    emails in the database.
    """
    
    def __init__(self, collection: AsyncIOMotorCollection):
        """
        Initialize the email repository.
        
        Args:
            collection: MongoDB collection instance
        """
        super().__init__(collection)
    
    async def find_by_user_id(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find emails by user ID.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of emails to return
            
        Returns:
            List[Dict[str, Any]]: List of emails
        """
        return await self.find_many({"user_id": user_id}, limit=limit)
    
    async def find_by_id(self, email_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Find an email by IMAP UID and user ID.
        
        Args:
            email_id: IMAP UID of the email
            user_id: ID of the user
            
        Returns:
            Optional[Dict[str, Any]]: Email if found, None otherwise
        """
        return await self.find_one({"email_id": email_id, "user_id": user_id})
    
    async def update_by_id(self, email_id: str, user_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update an email by IMAP UID and user ID.
        
        Args:
            email_id: IMAP UID of the email
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
    
    async def delete_by_id(self, email_id: str, user_id: str) -> bool:
        """
        Delete an email by IMAP UID and user ID.
        
        Args:
            email_id: IMAP UID of the email
            user_id: ID of the user
            
        Returns:
            bool: True if deletion successful
        """
        result = await self._collection.delete_one({"email_id": email_id, "user_id": user_id})
        return result.deleted_count > 0

    async def find_by_thread_id(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Find emails by thread ID.
        
        Args:
            thread_id: Thread ID to find emails for
            
        Returns:
            List[Dict[str, Any]]: List of matching emails
        """
        return await self.find_many({"thread_id": thread_id}) 