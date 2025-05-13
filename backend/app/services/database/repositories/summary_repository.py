"""
Repository for managing email summaries in MongoDB.
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime

from app.models.summary_models import SummarySchema
from app.services.database.repositories.base_repository import BaseRepository
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
        self.collection = collection
    
    async def setup_indexes(self):
        """Create indexes for the summary collection."""
        await self.collection.create_index("google_id")
        await self.collection.create_index([("email_id", 1), ("google_id", 1)], unique=True)
        await self.collection.create_index("generated_at")

    async def find_by_email_id(self, email_id: str) -> Optional[SummarySchema]:
        """
        Find a summary by email ID.
        
        Args:
            email_id: ID of the email
            
        Returns:
            Optional[SummarySchema]: Summary if found, None otherwise
        """
        return await self.find_one({"email_id": email_id})
    
    async def find_by_google_id(self, google_id: str) -> List[SummarySchema]:
        """
        Find summaries by Google user ID.
        
        Args:
            google_id: Google ID of the user
            
        Returns:
            List[SummarySchema]: List of summaries
        """
        return await self.find_many({"google_id": google_id})

    async def find_email_ids_by_keyword(self, google_id: str, keyword: str) -> List[str]:
        """
        Search for emails using summary keywords.

        Args:
            google_id: Google ID of the user.
            keyword: Keyword to search in the summary keywords.
            limit: Maximum number of emails to return.

        Returns:
            List[EmailSchema]: List of emails whose summaries match the keyword.
        """
        
        query = {
            "google_id": google_id,
            "keywords": {"$regex": keyword, "$options": "i"}
        }
        results = await self.find_many(query, projection={"email_id": 1})
        return [r["email_id"] for r in results]


    async def update_by_email_id(
        self, 
        email_id: str, 
        update_data: Dict[str, Any],
        upsert: bool = False
    ) -> bool:
        """
        Update a summary by email ID.
        
        Args:
            email_id: ID of the email
            update_data: Data to update
            upsert: If True, create a new document if no match is found
            
        Returns:
            bool: True if update successful
        """
        return await self.update_one(
            {"email_id": email_id},
            update_data,
            upsert=upsert
        )

    async def delete_by_email_and_google_id(self, email_id: str, google_id: str) -> bool:
        """
        Delete a summary by email ID and Google user ID.
        
        Args:
            email_id: ID of the email
            google_id: Google ID of the user
            
        Returns:
            bool: True if deletion successful
        """
        return await self.delete_one({"email_id": email_id, "google_id": google_id})

    async def find_many(
        self, 
        query: Dict[str, Any], 
        limit: int = 100, 
        skip: int = 0, 
        sort: List[tuple] = None,
        projection: Optional[Dict[str, int]] = None
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
        # Ensure datetime fields are properly handled
        if "generated_at" in query:
            if isinstance(query["generated_at"], dict):
                for op, value in query["generated_at"].items():
                    if isinstance(value, datetime):
                        query["generated_at"][op] = value
        
        return await super().find_many(query, limit, skip, sort, projection=projection) 