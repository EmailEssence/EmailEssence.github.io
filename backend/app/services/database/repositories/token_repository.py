"""
Repository for managing OAuth tokens in MongoDB.
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from app.models.auth_models import TokenData
from app.services.database.repositories.base_repository import BaseRepository
from app.services.database.interfaces import ITokenRepository

class TokenRepository(BaseRepository[TokenData], ITokenRepository):
    """
    Repository for managing OAuth tokens in MongoDB.
    
    This class provides methods for storing, retrieving, and managing
    OAuth tokens in the database.
    """
    
    def __init__(self, collection: AsyncIOMotorCollection):
        """
        Initialize the token repository.
        
        Args:
            collection: MongoDB collection instance
        """
        super().__init__(collection, TokenData)
        self.collection = collection
    
    async def setup_indexes(self):
        """Create indexes for the token collection."""
        await self.collection.create_index("google_id", unique=True)
        await self.collection.create_index("token", unique=True)
    
    async def find_by_google_id(self, google_id: str) -> Optional[TokenData]:
        """
        Find a token by Google ID.
        
        Args:
            google_id: Google ID to search for
            
        Returns:
            Optional[TokenData]: Token if found, None otherwise
        """
        doc = await self.find_one({"google_id": google_id})
        if doc:
            if isinstance(doc, TokenData):
                return doc
            return TokenData(**doc)
        return None
    
    async def find_by_token(self, token: str) -> Optional[TokenData]:
        """
        Find a token by access token.
        
        Args:
            token: Access token to search for
            
        Returns:
            Optional[TokenData]: Token if found, None otherwise
        """
        return await self.find_one({"token": token})
    
    async def insert_one(self, token: TokenData) -> str:
        """
        Insert a new token or update if it already exists.
        
        Args:
            token: Token to insert/update
            
        Returns:
            str: ID of the token
        """
        return await self.upsert_one(
            {"google_id": token.google_id},
            token.model_dump()
        )
    
    async def update_by_google_id(self, google_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a token by Google ID.
        
        Args:
            google_id: Google ID of the token to update
            update_data: Data to update
            
        Returns:
            bool: True if update was successful
        """
        result = await self.upsert_one(
            {"google_id": google_id},
            update_data
        )
        return result is not None
    
    async def delete_by_google_id(self, google_id: str) -> bool:
        """
        Delete a token by Google ID.
        
        Args:
            google_id: Google ID of the token to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            result = await self.collection.delete_one({"google_id": google_id})
            return result.deleted_count > 0
        except Exception as e:
            raise 