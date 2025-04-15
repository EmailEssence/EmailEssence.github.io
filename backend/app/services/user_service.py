import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends
from bson import ObjectId

from app.models import UserSchema, OAuthSchema
from app.services.database import UserRepository, get_user_repository

logger = logging.getLogger(__name__)

class UserService:
    """
    Service for managing user data and operations.
    
    This class provides methods for user management, including
    creation, retrieval, updates, and deletion of user records.
    """
    
    def __init__(self, user_repo: UserRepository = Depends(get_user_repository)):
        """Initialize the user service with required configuration"""
        self.user_repo = user_repo

    async def get_or_create_user(self, user_info: Dict[str, Any], credentials: Any = None) -> Dict[str, Any]:
        """Finds or creates a user in the database based on Google OAuth data."""
        try:
            google_id = user_info["id"]
            logger.debug(f"Checking if user with Google ID {google_id} exists")

            existing_user = await self.user_repo.find_one({"google_id": google_id})

            if existing_user:
                existing_user["_id"] = str(existing_user["_id"])
                logger.info(f"User found: {existing_user['email']}")
                return existing_user

            logger.info(f"Creating new user with email: {user_info['email']}")

            # Create OAuth data dict if credentials are provided
            oauth_data = {}
            if credentials:
                oauth_data = OAuthSchema(
                    token=credentials.token,
                    refresh_token=credentials.refresh_token,
                    token_uri=credentials.token_uri,
                    client_id=credentials.client_id,
                    client_secret=credentials.client_secret,
                    scopes=credentials.scopes
                )
            
            logger.debug(f"OAuth credentials included for {user_info['email']}")

            # Create new user record
            new_user = UserSchema(
                google_id=google_id,
                email=user_info["email"],
                name=user_info.get("name", user_info.get("email").split("@")[0]),
                oauth=oauth_data
            )

            # Insert into MongoDB
            inserted_id = await self.user_repo.insert_one(new_user.model_dump())
            logger.info(f"User inserted with ID: {inserted_id}")

            new_user_dict = new_user.model_dump()
            new_user_dict["_id"] = str(inserted_id)
            return new_user_dict
        except Exception as e:
            logger.error(f"Failed to get or create user: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by ID."""
        try:
            logger.debug(f"Fetching user by ID: {user_id}")

            if not ObjectId.is_valid(user_id):
                logger.warning("Invalid ObjectId format")
                return None
            
            user = await self.user_repo.find_one({"_id": ObjectId(user_id)})
            
            if user:
                user["_id"] = str(user["_id"])
                logger.info(f"User found: {user.get('email', 'Unknown')}")
            else:
                logger.warning("User not found")
            
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a user's information."""
        try:
            logger.debug(f"Updating user with ID: {user_id}")

            if not ObjectId.is_valid(user_id):
                logger.warning("Invalid ObjectId format")
                return None
            
            result = await self.user_repo.update_one({"_id": ObjectId(user_id)}, user_data)
            
            if result.modified_count == 0:
                logger.warning("No modifications made")
                return None
            
            logger.info(f"User {user_id} updated successfully")
            return await self.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user from the database."""
        try:
            logger.info(f"Attempting to delete user with ID: {user_id}")

            if not ObjectId.is_valid(user_id):
                logger.warning("Invalid ObjectId format")
                return False

            result = await self.user_repo.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user_preferences(self, google_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve only user preferences."""
        try:
            logger.debug(f"Fetching preferences for Google ID: {google_id}")
            user = await self.user_repo.find_one(
                {"google_id": google_id},
                projection={"preferences": 1, "_id": 0}
            )
            return user.get("preferences", {}) if user else None
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_user_preferences(self, google_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences."""
        try:
            logger.debug(f"Updating preferences for Google ID: {google_id}")

            result = await self.user_repo.update_one(
                {"google_id": google_id},
                {"$set": {"preferences": preferences}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
            raise HTTPException(status_code=500, detail=str(e))
