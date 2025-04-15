"""
Repository for managing users in MongoDB.
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from app.models.user_models import UserSchema
from app.services.database.base_repository import BaseRepository
from app.services.database.interfaces import IUserRepository

class UserRepository(BaseRepository[UserSchema], IUserRepository):
    """
    Repository for managing users in MongoDB.
    
    This class provides methods for storing, retrieving, and managing
    users in the database.
    """
    
    def __init__(self, collection: AsyncIOMotorCollection):
        """
        Initialize the user repository.
        
        Args:
            collection: MongoDB collection instance
        """
        super().__init__(collection, UserSchema)
    
    async def ensure_indexes(self):
        """
        Ensure that required indexes exist.
        This should be called after the repository is initialized.
        """
        await self._collection.create_index("email", unique=True)
        await self._collection.create_index("google_id", unique=True)
    
    async def find_by_email(self, email: str) -> Optional[UserSchema]:
        """
        Find a user by email.
        
        Args:
            email: Email address to search for
            
        Returns:
            Optional[UserSchema]: User if found, None otherwise
        """
        return await self.find_one({"email": email})
    
    async def find_by_username(self, username: str) -> Optional[UserSchema]:
        """
        Find a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            Optional[UserSchema]: User if found, None otherwise
        """
        return await self.find_one({"username": username})

    async def find_by_google_id(self, google_id: str) -> Optional[UserSchema]:
        """
        Find a user by Google ID.
        
        Args:
            google_id: Google ID to search for
            
        Returns:
            Optional[UserSchema]: User if found, None otherwise
        """
        return await self.find_one({"google_id": google_id})

    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences.
        
        Args:
            user_id: ID of the user
            preferences: New preferences to set
            
        Returns:
            bool: True if update successful
        """
        result = await self._collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"preferences": preferences}}
        )
        return result.modified_count > 0

    async def insert_one(self, user: UserSchema) -> str:
        """
        Insert a single user.
        
        Args:
            user: User to insert
            
        Returns:
            str: ID of the inserted user
        """
        return await super().insert_one(user)

    async def update_by_email(self, email: str, user_data: Dict[str, Any]) -> bool:
        """
        Update a user by email.
        
        Args:
            email: Email address to update user for
            user_data: New user data
            
        Returns:
            bool: True if update successful
        """
        result = await self._collection.update_one(
            {"email": email},
            {"$set": user_data}
        )
        return result.modified_count > 0
    
    async def delete_by_email(self, email: str) -> bool:
        """
        Delete a user by email.
        
        Args:
            email: Email address to delete user for
            
        Returns:
            bool: True if deletion successful
        """
        result = await self._collection.delete_one({"email": email})
        return result.deleted_count > 0

    async def find_by_id(self, id: str) -> Optional[UserSchema]:
        """
        Find a user by ID (either MongoDB ObjectId or Google ID).
        
        Args:
            id: User ID (MongoDB ObjectId or Google ID)
            
        Returns:
            Optional[UserSchema]: User if found, None otherwise
        """
        # Try MongoDB ObjectId first
        if ObjectId.is_valid(id):
            user = await self.find_one({"_id": ObjectId(id)})
            if user:
                return user
        
        # Try Google ID if not found or not a valid ObjectId
        return await self.find_one({"google_id": id})

    async def update_one(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a user by ID (either MongoDB ObjectId or Google ID).
        
        Args:
            document_id: User ID (MongoDB ObjectId or Google ID)
            update_data: Data to update
            
        Returns:
            bool: True if update successful
        """
        # Try MongoDB ObjectId first
        if ObjectId.is_valid(document_id):
            result = await self._collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                return True
        
        # Try Google ID if not found or not a valid ObjectId
        result = await self._collection.update_one(
            {"google_id": document_id},
            {"$set": update_data}
        )
        return result.modified_count > 0 