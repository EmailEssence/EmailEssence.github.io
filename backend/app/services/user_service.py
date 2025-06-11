"""
User service for handling user-related operations.
"""

# Standard library imports
from typing import Optional, Dict, Any

# Third-party imports
from fastapi import HTTPException, status

# Internal imports
from app.utils.helpers import get_logger, log_operation, standardize_error_response
from app.models import UserSchema, PreferencesSchema
from app.services.database import get_user_repository, UserRepository

# -------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------

logger = get_logger(__name__, 'service')

class UserService:
    """
    Service for handling user-related operations.
    
    This class provides methods for user management, including:
    - Creating and retrieving users
    - Updating user information
    - Managing user authentication state
    """
    
    def __init__(self, user_repository: UserRepository = None):
        """
        Initialize the user service.
        
        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository or get_user_repository()

    async def get_user(self, user_id: str) -> Optional[UserSchema]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        try:
            return await self.user_repository.find_by_id(user_id)
        except Exception as e:
            raise standardize_error_response(e, "get user", user_id)

    async def get_user_by_email(self, email: str) -> Optional[UserSchema]:
        """
        Get a user by email.
        
        Args:
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        try:
            return await self.user_repository.find_by_email(email)
        except Exception as e:
            raise standardize_error_response(e, "get user by email", email)

    async def create_user(self, user_data: Dict[str, Any]) -> UserSchema:
        """
        Create a new user.
        
        Args:
            user_data: User data
            
        Returns:
            Created user
        """
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
                "preferences": PreferencesSchema().model_dump()
            }
            
            # Update with any provided values
            complete_user_data.update(user_data)
            
            # Create UserSchema instance
            user = UserSchema(**complete_user_data)
            
            # Insert into database
            user_id = await self.user_repository.insert_one(user)
            user._id = user_id
            
            log_operation(logger, 'info', f"Created user: {user.email}")
            return user
        except Exception as e:
            raise standardize_error_response(e, "create user", user_data.get("email"))

    async def update_user(self, google_id: str, user_data: Dict[str, Any]) -> Optional[UserSchema]:
        """
        Update a user.
        
        Args:
            google_id: User Google ID
            user_data: Updated user data
            
        Returns:
            Optional[UserSchema]: Updated user if successful, None otherwise
        """
        try:
            # First get the current user to ensure it exists
            current_user = await self.user_repository.find_by_id(google_id)
            if not current_user:
                log_operation(logger, 'warning', f"User not found: {google_id}")
                return None

            # Update the user
            success = await self.user_repository.update_one(google_id, user_data)
            if not success:
                log_operation(logger, 'warning', f"Update failed for user: {google_id}")
                return None

            # Get the updated user
            updated_user = await self.user_repository.find_by_id(google_id)
            if not updated_user:
                log_operation(logger, 'warning', f"Failed to fetch updated user: {google_id}")
                return None

            log_operation(logger, 'info', f"Updated user: {google_id}")
            return UserSchema(**updated_user)
        except Exception as e:
            raise standardize_error_response(e, "update user", google_id)

    async def delete_user(self, google_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            google_id: User Google ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.user_repository.delete_by_google_id(google_id)
            if result:
                log_operation(logger, 'info', f"Deleted user: {google_id}")
            return result
        except Exception as e:
            raise standardize_error_response(e, "delete user", google_id)

    async def get_preferences(self, google_id: str) -> Dict[str, Any]:
        """
        Get user preferences.
        
        Args:
            google_id: User's Google ID
            
        Returns:
            Dict[str, Any]: User preferences
        """
        try:
            log_operation(logger, 'debug', f"Fetching preferences for Google ID: {google_id}")
            user = await self.user_repository.find_one({"google_id": google_id})
            return user.get("preferences", {}) if user else {}
        except Exception as e:
            raise standardize_error_response(e, "get preferences", google_id)

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
            log_operation(logger, 'debug', f"Updating preferences for Google ID: {google_id}")
            result = await self.user_repository.update_one(
                {"google_id": google_id},
                {"$set": {"preferences": preferences}}
            )
            if result:
                log_operation(logger, 'info', f"Updated preferences for user: {google_id}")
            return result
        except Exception as e:
            raise standardize_error_response(e, "update preferences", google_id)
