"""
Repository for managing OAuth tokens in MongoDB.
"""

from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
import logging

from app.models import TokenData
from app.services.database.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class TokenRepository(BaseRepository):
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
        super().__init__(collection)
    
    async def find_by_email(self, email: str) -> Optional[TokenData]:
        """
        Find tokens by email.
        
        Args:
            email: Email address to find tokens for
            
        Returns:
            Optional[TokenData]: Token data if found, None otherwise
        """
        logger.debug(f"Looking up tokens for email: {email}")
        token_data = await self.find_one({"email": email})
        if token_data:
            logger.info(f"Found tokens for email: {email}")
            return TokenData(**token_data)
        else:
            logger.warning(f"No tokens found for email: {email}")
            return None
    
    async def update_by_email(self, email: str, token_data: Dict[str, Any]) -> bool:
        """
        Update tokens by email. Creates the document if it doesn't exist.
        
        Args:
            email: Email address to update tokens for
            token_data: New token data
            
        Returns:
            bool: True if update/insert successful
        """
        logger.debug(f"Updating tokens for email: {email}")
        # Validate token data against TokenData model
        token_data_model = TokenData(**token_data)
        result = await self._collection.update_one(
            {"email": email},
            {"$set": token_data_model.dict()},
            upsert=True  # Create document if it doesn't exist
        )
        success = result.modified_count > 0 or result.upserted_id is not None
        if success:
            logger.info(f"Successfully {'created' if result.upserted_id else 'updated'} tokens for email: {email}")
        else:
            logger.warning(f"No tokens updated for email: {email}")
        return success
    
    async def delete_by_email(self, email: str) -> bool:
        """
        Delete tokens by email.
        
        Args:
            email: Email address to delete tokens for
            
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