from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from app.models import SummarySchema
from app.services.database.base_repository import BaseRepository
from app.services.database.interfaces import ISummaryRepository

class SummaryRepository(BaseRepository[SummarySchema], ISummaryRepository):
    """
    Summary repository implementation for handling summary-related database operations.
    
    Args:
        collection: MongoDB collection instance (defaults to db.summaries)
    """
    def __init__(self, collection: AsyncIOMotorCollection = None):
        from database import db
        collection = collection or db.summaries
        super().__init__(collection, SummarySchema)
    
    async def find_by_email_id(self, email_id: str) -> Optional[SummarySchema]:
        """Find a summary by its associated email_id"""
        return await self.find_one({"email_id": email_id})
    
    async def find_by_user_id(self, user_id: str) -> List[SummarySchema]:
        """Find all summaries for a specific user"""
        return await self.find_many({"user_id": user_id}) 