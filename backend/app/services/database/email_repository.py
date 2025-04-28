"""
Repository for managing emails in MongoDB.
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from app.models.email_models import EmailSchema
from app.services.database.base_repository import BaseRepository
from app.services.database.interfaces import IEmailRepository

class EmailRepository(BaseRepository[EmailSchema], IEmailRepository):
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
        super().__init__(collection, EmailSchema)
        self.collection = collection
    
    async def setup_indexes(self):
        await self.collection.create_index("google_id")
        await self.collection.create_index([("email_id", 1), ("google_id", 1)], unique=True)
        await self.collection.create_index("thread_id")
        await self.collection.create_index("is_read")
    
    async def find_by_google_id(self, google_id: str, limit: int = 100) -> List[EmailSchema]:
        """
        Find emails by Google user ID.
        
        Args:
            google_id: Google ID of the user
            limit: Maximum number of emails to return
            
        Returns:
            List[EmailSchema]: List of emails
        """
        return await self.find_many({"google_id": google_id}, limit=limit)
    
    async def find_by_email_and_google_id(self, email_id: str, google_id: str) -> Optional[EmailSchema]:
        """
        Find an email by IMAP UID and Google user ID.
        
        Args:
            email_id: IMAP UID of the email
            google_id: Google ID of the user
            
        Returns:
            Optional[EmailSchema]: Email if found, None otherwise
        """
        return await self.find_one({"email_id": email_id, "google_id": google_id})
    
    async def update_by_email_and_google_id(
        self, 
        email_id: str, 
        google_id: str, 
        update_data: Dict[str, Any]
    ) -> bool:
        """
        Update an email by IMAP UID and Google user ID.
        
        Args:
            email_id: IMAP UID of the email
            google_id: Google ID of the user
            update_data: Data to update
            
        Returns:
            bool: True if update successful
        """
        return await self.update_one(
            {"email_id": email_id, "google_id": google_id},
            update_data
        )
    
    async def delete_by_email_and_google_id(self, email_id: str, google_id: str) -> bool:
        """
        Delete an email by IMAP UID and Google user ID.
        
        Args:
            email_id: IMAP UID of the email
            google_id: Google ID of the user
            
        Returns:
            bool: True if deletion successful
        """
        return await self.delete_one({"email_id": email_id, "google_id": google_id})

    async def find_by_thread_id(self, thread_id: str) -> List[EmailSchema]:
        """
        Find emails by thread ID.
        
        Args:
            thread_id: Thread ID to find emails for
            
        Returns:
            List[EmailSchema]: List of matching emails
        """
        return await self.find_many({"thread_id": thread_id})

    async def find_by_email_id(self, email_id: str) -> Optional[EmailSchema]:
        """
        Find an email by email ID.
        
        Args:
            email_id: Email ID to search for
            
        Returns:
            Optional[EmailSchema]: Email if found, None otherwise
        """
        return await self.find_one({"email_id": email_id})

    async def find_unread(self) -> List[EmailSchema]:
        """
        Find all unread emails.
        
        Returns:
            List[EmailSchema]: List of unread emails
        """
        return await self.find_many({"is_read": False})

    async def mark_as_read(self, email_id: str) -> Optional[EmailSchema]:
        """
        Mark an email as read.
        
        Args:
            email_id: ID of the email to mark as read
            
        Returns:
            Optional[EmailSchema]: Updated email if found, None otherwise
        """
        if await self.update_one(
            {"email_id": email_id},
            {"$set": {"is_read": True}}
        ):
            return await self.find_by_email_id(email_id)
        return None 