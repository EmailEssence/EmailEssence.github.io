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
    
    async def find_by_google_id(self, google_id: str, limit: int = 100) -> List[EmailSchema]:
        """
        Find emails by Google user ID.
        
        Args:
            google_id: Google ID of the user
            limit: Maximum number of emails to return
            
        Returns:
            List[EmailSchema]: List of emails
        """
        docs = await self.find_many({"google_id": google_id}, limit=limit)
        return [self._model_class(**doc) for doc in docs]
    
    async def find_by_id(self, email_id: str, google_id: str) -> Optional[EmailSchema]:
        """
        Find an email by IMAP UID and Google user ID.
        
        Args:
            email_id: IMAP UID of the email
            google_id: Google ID of the user
            
        Returns:
            Optional[EmailSchema]: Email if found, None otherwise
        """
        doc = await self.find_one({"email_id": email_id, "google_id": google_id})
        if doc:
            # If doc is already an EmailSchema instance, return it directly
            if isinstance(doc, EmailSchema):
                return doc
            # Otherwise convert dict to EmailSchema
            return self._model_class(**doc)
        return None
    
    async def update_by_id(self, email_id: str, google_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update an email by IMAP UID and Google user ID.
        
        Args:
            email_id: IMAP UID of the email
            google_id: Google ID of the user
            update_data: Data to update
            
        Returns:
            bool: True if update successful
        """
        result = await self._collection.update_one(
            {"email_id": email_id, "google_id": google_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete_by_id(self, email_id: str, google_id: str) -> bool:
        """
        Delete an email by IMAP UID and Google user ID.
        
        Args:
            email_id: IMAP UID of the email
            google_id: Google ID of the user
            
        Returns:
            bool: True if deletion successful
        """
        result = await self._collection.delete_one({"email_id": email_id, "google_id": google_id})
        return result.deleted_count > 0

    async def find_by_thread_id(self, thread_id: str) -> List[EmailSchema]:
        """
        Find emails by thread ID.
        
        Args:
            thread_id: Thread ID to find emails for
            
        Returns:
            List[EmailSchema]: List of matching emails
        """
        docs = await self.find_many({"thread_id": thread_id})
        return [self._model_class(**doc) for doc in docs]

    async def insert_one(self, email: EmailSchema) -> str:
        """
        Insert a single email.
        
        Args:
            email: Email to insert
            
        Returns:
            str: ID of the inserted email
        """
        return await super().insert_one(email.model_dump())

    async def find_by_email_id(self, email_id: str) -> Optional[EmailSchema]:
        """
        Find an email by email ID.
        
        Args:
            email_id: Email ID to search for
            
        Returns:
            Optional[EmailSchema]: Email if found, None otherwise
        """
        doc = await self.find_one({"email_id": email_id})
        return self._model_class(**doc) if doc else None

    async def find_unread(self) -> List[EmailSchema]:
        """
        Find all unread emails.
        
        Returns:
            List[EmailSchema]: List of unread emails
        """
        docs = await self.find_many({"is_read": False})
        return [self._model_class(**doc) for doc in docs]

    async def mark_as_read(self, email_id: str) -> Optional[EmailSchema]:
        """
        Mark an email as read.
        
        Args:
            email_id: ID of the email to mark as read
            
        Returns:
            Optional[EmailSchema]: Updated email if found, None otherwise
        """
        result = await self._collection.update_one(
            {"email_id": email_id},
            {"$set": {"is_read": True}}
        )
        if result.modified_count > 0:
            return await self.find_by_email_id(email_id)
        return None 