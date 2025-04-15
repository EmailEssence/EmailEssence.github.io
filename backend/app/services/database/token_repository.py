"""
Token repository for handling token-related database operations.
"""

from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId

from app.services.database.base_repository import BaseRepository
from app.models import TokenSchema

class TokenRepository(BaseRepository[TokenSchema]):
    """
    Repository for handling token-related database operations.
    
    Args:
        collection: MongoDB collection instance
    """
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, TokenSchema)
        
    async def find_by_email(self, email: str) -> Optional[TokenSchema]:
        """
        Find a token record by user email.
        
        Args:
            email: User's email address
            
        Returns:
            Optional[TokenSchema]: Token record if found, None otherwise
        """
        return await self.find_one({"email": email})
        
    async def find_by_token(self, token: str) -> Optional[TokenSchema]:
        """
        Find a token record by token string.
        
        Args:
            token: Token string to search for
            
        Returns:
            Optional[TokenSchema]: Token record if found, None otherwise
        """
        return await self.find_one({"token": token})
        
    async def update_by_email(self, email: str, token_data: Dict[str, Any]) -> bool:
        """
        Update a token record by user email.
        
        Args:
            email: User's email address
            token_data: Token data to update
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        result = await self.update_one(
            {"email": email},
            token_data,
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
        
    async def delete_by_email(self, email: str) -> bool:
        """
        Delete a token record by user email.
        
        Args:
            email: User's email address
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        result = await self.delete_one({"email": email})
        return result.deleted_count > 0 