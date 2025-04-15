from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from app.models import EmailSchema
from app.services.database.base_repository import BaseRepository
from app.services.database.interfaces import IEmailRepository

class EmailRepository(BaseRepository[EmailSchema], IEmailRepository):
    """
    Email repository implementation for handling email-related database operations.
    
    Args:
        collection: MongoDB collection instance (defaults to db.emails)
    """
    def __init__(self, collection: AsyncIOMotorCollection = None):
        from database import db
        collection = collection or db.emails
        super().__init__(collection, EmailSchema)
    
    async def find_by_email_id(self, email_id: str) -> Optional[EmailSchema]:
        """Find an email by its email_id"""
        data = await self.db_service.find_one({"email_id": email_id})
        if data and "from" in data:
            data["from_"] = data.pop("from")
        return self._to_model(data)
    
    async def find_unread(self) -> List[EmailSchema]:
        """Find all unread emails"""
        data_list = await self.db_service.find_many({"is_read": False})
        result = []
        for data in data_list:
            if "from" in data:
                data["from_"] = data.pop("from")
            result.append(self._to_model(data))
        return result
    
    async def mark_as_read(self, email_id: str) -> Optional[EmailSchema]:
        """Mark an email as read and return the updated email"""
        email = await self.find_by_email_id(email_id)
        if email:
            email.is_read = True
            await self.update_one({"email_id": email_id}, email)
        return email 