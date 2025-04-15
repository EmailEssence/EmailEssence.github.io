import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from bson import ObjectId
from google.oauth2.credentials import Credentials

from app.models import UserSchema, TokenData, PreferencesSchema
from app.services.database.user_repository import UserRepository
from app.services.database.factories import get_user_repository

logger = logging.getLogger(__name__)

class UserService:
    """
    Service for handling user-related operations.
    
    This class provides methods for user management, including:
    - Creating and retrieving users
    - Updating user information
    - Managing user authentication state
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize the user service.
        
        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository
        # Note: We can't call ensure_indexes here because it's async
        # The indexes will be created on first use

    async def get_user(self, user_id: str) -> Optional[UserSchema]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        try:
            user_data = await self.user_repository.find_by_id(user_id)
            if not user_data:
                return None
            return UserSchema(**user_data)
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user"
            )

    async def get_user_by_email(self, email: str) -> Optional[UserSchema]:
        """
        Get a user by email.
        
        Args:
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        try:
            user_data = await self.user_repository.find_by_email(email)
            if not user_data:
                return None
            return UserSchema(**user_data)
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user by email"
            )

    async def create_user(self, user_data: Dict[str, Any]) -> UserSchema:
        """
        Create a new user.
        
        Args:
            user_data: User data
            
        Returns:
            Created user
        """
        # Ensure indexes exist before creating user
        await self.user_repository.ensure_indexes()
        
        try:
            # Create a complete user data dictionary with all required fields
            complete_user_data = {
                "google_id": user_data.get("google_id", ""),
                "email": user_data.get("email", ""),
                "name": user_data.get("name", ""),
                "oauth": {
                    "token": "",
                    "refresh_token": None,
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": "",
                    "client_secret": "",
                    "scopes": []
                },
                "preferences": PreferencesSchema().dict()
            }
            
            # Update with any provided values
            complete_user_data.update(user_data)
            
            # Insert into database
            user_id = await self.user_repository.insert_one(complete_user_data)
            complete_user_data["_id"] = user_id
            
            # Return as UserSchema
            return UserSchema(**complete_user_data)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[UserSchema]:
        """
        Update a user.
        
        Args:
            user_id: User ID
            user_data: Updated user data
            
        Returns:
            Optional[UserSchema]: Updated user if successful, None otherwise
        """
        try:
            # First get the current user to ensure it exists
            current_user = await self.user_repository.find_by_id(user_id)
            if not current_user:
                logger.error(f"User not found: {user_id}")
                return None

            # Update the user
            success = await self.user_repository.update_one(user_id, user_data)
            if not success:
                logger.error(f"Update failed for user: {user_id}")
                return None

            # Get the updated user
            updated_user = await self.user_repository.find_by_id(user_id)
            if not updated_user:
                logger.error(f"Failed to fetch updated user: {user_id}")
                return None

            return UserSchema(**updated_user)
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            return await self.user_repository.delete_one(user_id)
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )

    async def get_preferences(self, google_id: str) -> Dict[str, Any]:
        """
        Get user preferences.
        
        Args:
            google_id: User's Google ID
            
        Returns:
            Dict[str, Any]: User preferences
        """
        try:
            logger.debug(f"Fetching preferences for Google ID: {google_id}")
            user = await self.user_repository.find_one({"google_id": google_id})
            return user.get("preferences", {}) if user else {}
        except Exception as e:
            logger.error(f"Failed to get preferences: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get preferences"
            )

    async def update_preferences(self, google_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences.
        
        Args:
            google_id: User's Google ID
            preferences: New preferences
            
        Returns:
            bool: True if update successful
        """
        try:
            logger.debug(f"Updating preferences for Google ID: {google_id}")
            result = await self.user_repository.update_one(
        {"google_id": google_id},
        {"$set": {"preferences": preferences}}
    )
            return result
        except Exception as e:
            logger.error(f"Failed to update preferences: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preferences"
            )
