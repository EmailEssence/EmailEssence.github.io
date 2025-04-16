"""
Repository for managing OAuth tokens in MongoDB.
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
import logging

from app.models.auth_models import TokenData
from app.services.database.base_repository import BaseRepository
from app.services.database.interfaces import ITokenRepository

logger = logging.getLogger(__name__)

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
    
    async def find_by_email(self, email: str) -> Optional[TokenData]:
        """
        Find a token by email.
        
        Args:
            email: Email address to search for
            
        Returns:
            Optional[TokenData]: Token if found, None otherwise
        """
        logger.debug(f"Looking up tokens for email: {email}")
        doc = await self.find_one({"email": email})
        if doc:
            logger.info(f"Found tokens for email: {email}")
            # If doc is already a TokenData instance, return it directly
            if isinstance(doc, TokenData):
                return doc
            # Otherwise convert dict to TokenData
            return self._model_class(**doc)
        else:
            logger.warning(f"No tokens found for email: {email}")
            return None
    
    async def find_by_token(self, token: str) -> Optional[TokenData]:
        """
        Find a token by token string.
        
        Args:
            token: Token string to search for
            
        Returns:
            Optional[TokenData]: Token if found, None otherwise
        """
        doc = await self.find_one({"token": token})
        return self._model_class(**doc) if doc else None

    async def insert_one(self, token: TokenData) -> str:
        """
        Insert a single token.
        
        Args:
            token: Token to insert
            
        Returns:
            str: ID of the inserted token
        """
        return await super().insert_one(token.model_dump())

    async def update_by_email(self, email: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a token by email.
        
        Args:
            email: Email address
            update_data: Data to update
            
        Returns:
            bool: True if update successful
        """
        logger.debug(f"Updating tokens for email: {email}")
        result = await self._collection.update_one(
            {"email": email},
            {"$set": update_data}
        )
        success = result.modified_count > 0
        if success:
            logger.info(f"Successfully updated tokens for email: {email}")
        else:
            logger.warning(f"No tokens updated for email: {email}")
        return success

    async def delete_by_email(self, email: str) -> bool:
        """
        Delete a token by email.
        
        Args:
            email: Email address
            
        Returns:
            bool: True if deletion successful
        """
        logger.debug(f"Deleting tokens for email: {email}")
        result = await self._collection.delete_one({"email": email})
        success = result.deleted_count > 0
        if success:
            logger.info(f"Successfully deleted tokens for email: {email}")
        else:
            logger.warning(f"No tokens deleted for email: {email}")
        return success 