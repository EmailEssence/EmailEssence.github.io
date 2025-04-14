import logging
from database import db
from app.models.user_model import UserSchema, OAuthSchema
from app.services.database_service import DatabaseService
from bson import ObjectId

logger = logging.getLogger(__name__)
# Debugging helper function
def debug(message: str):
    logger.debug(message)
    
user_db = DatabaseService(db.users)


async def get_or_create_user(user_info, credentials=None):
    """Finds or creates a user in the database based on Google OAuth data."""
    google_id = user_info["id"]  # Unique Google ID
    logger.debug(f"[DB FETCH] Checking if user with Google ID {google_id} exists...")

    existing_user = await user_db.find_one({"google_id": google_id})

    if existing_user:
        # Convert _id to string for JSON serialization
        existing_user["_id"] = str(existing_user["_id"])
        logger.info(f"[FOUND] User found: {existing_user['email']}")
        return existing_user

    logger.info(f"[DB INSERT] Creating new user with email: {user_info['email']}")

    # Create OAuth data dict if credentials are provided
    # Currently passes OAuth object directly to the schema
    oauth_data = {}
    if credentials:
        oauth_data = OAuthSchema(
        token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_uri=credentials.token_uri,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        scopes=credentials.scopes  # Handles list correctly
    ) if credentials else None
    
    logger.debug(f"[OAUTH] OAuth credentials included for {user_info['email']}")

    # Create new user record
    new_user = UserSchema(
        google_id=google_id,
        email=user_info["email"],
        name=user_info.get("name", user_info.get("email").split("@")[0]),
        oauth=oauth_data
    )

    # Insert into MongoDB
    inserted_id = await user_db.insert_one(new_user.model_dump())
    logger.info(f"[DB INSERT] User inserted with ID: {inserted_id.inserted_id}")

    new_user_dict = new_user.model_dump()
    new_user_dict["_id"] = str(inserted_id.inserted_id)  # Convert ObjectId to string
    return new_user_dict

async def get_user_by_id(user_id: str):
    """Retrieve user by ID."""
    logger.debug(f"[DB FETCH] Fetching user by ID: {user_id}")

    if not ObjectId.is_valid(user_id):
        logger.warning("[VALIDATION] Invalid ObjectId format")
        return None
    
    user = await user_db.find_one({"_id": ObjectId(user_id)})
    
    if user:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string for frontend compatibility
        logger.info(f"[DB FETCH] User found: {user.get('email', 'Unknown')}")
    else:
        logger.warning("[NOT FOUND] User not found")
    
    return user

async def update_user(user_id: str, user_data: dict):
    """Update a user's information."""
    logger.debug(f"[DB UPDATE] Updating user with ID: {user_id}")

    if not ObjectId.is_valid(user_id):
        logger.warning("[VALIDATION] Invalid ObjectId format")
        return None
    
    result = await user_db.update_one({"_id": ObjectId(user_id)}, user_data)
    
    if result.modified_count == 0:
        logger.warning("[DB UPDATE] No modifications made")
        return None  # No update performed
    
    logger.info(f"[DB UPDATE] User {user_id} updated successfully")
    return await get_user_by_id(user_id)

async def delete_user(user_id: str):
    """Delete a user from the database."""
    logger.info(f"[DB DELETE] Attempting to delete user with ID: {user_id}")

    if not ObjectId.is_valid(user_id):
        logger.warning("[VALIDATION] Invalid ObjectId format")
        return False

    result = await user_db.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0


async def get_user_preferences(google_id: str):
    """Retrieve only user preferences."""
    logger.debug(f"[DB FETCH] Fetching preferences for Google ID: {google_id}")  
    user = await user_db.collection.find_one({"google_id": google_id}, {"preferences": 1, "_id": 0})
    return user.get("preferences", {}) if user else None
    

async def update_user_preferences(google_id: str, preferences: dict):
    """Update user preferences."""
    logger.debug(f"[DB UPDATE] Updating preferences for Google ID: {google_id}")

    result = user_db.update_one(
        {"google_id": google_id},
        {"$set": {"preferences": preferences}}
    )
    
    return result.modified_count > 0
