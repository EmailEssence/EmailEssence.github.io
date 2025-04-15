from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from app.models.user_model import UserSchema
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces import IUserRepository

class UserRepository(BaseRepository[UserSchema], IUserRepository):
    """
    User repository implementation for handling user-related database operations.
    
    Args:
        collection: MongoDB collection instance (defaults to db.users)
    """
    def __init__(self, collection: AsyncIOMotorCollection = None):
        from database import db
        collection = collection or db.users
        super().__init__(collection, UserSchema)
    
    async def find_by_email(self, email: str) -> Optional[UserSchema]:
        """Find a user by their email address"""
        return await self.find_one({"email": email})
    
    async def find_by_username(self, username: str) -> Optional[UserSchema]:
        """Find a user by their username"""
        return await self.find_one({"username": username}) 