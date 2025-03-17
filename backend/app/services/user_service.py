from database import db
from app.models.user_model import UserSchema
from bson import ObjectId

async def get_or_create_user(user_info, credentials=None):
    """Finds or creates a user in the database based on Google OAuth data."""
    google_id = user_info["id"]  # Unique Google ID
    existing_user = await db.users.find_one({"google_id": google_id})

    if existing_user:
        # Convert _id to string for JSON serialization
        existing_user["_id"] = str(existing_user["_id"])
        return existing_user

    # Create OAuth data dict if credentials are provided
    oauth_data = {}
    if credentials:
        oauth_data = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }

    # Create new user record
    new_user = UserSchema(
        google_id=google_id,
        email=user_info["email"],
        name=user_info.get("name", user_info.get("email").split("@")[0]),
        oauth=oauth_data
    )

    # Insert into MongoDB
    inserted_id = await db.users.insert_one(new_user.model_dump())
    new_user_dict = new_user.model_dump()
    new_user_dict["_id"] = str(inserted_id.inserted_id)  # Convert ObjectId to string
    return new_user_dict

async def get_user_by_id(user_id: str):
    """Retrieve user by ID."""
    if not ObjectId.is_valid(user_id):
        return None
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string for frontend compatibility
    return user


async def update_user(user_id: str, user_data: dict):
    """Update a user's information."""
    if not ObjectId.is_valid(user_id):
        return None
    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
    if result.modified_count == 0:
        return None  # No update performed
    return await get_user_by_id(user_id)


async def delete_user(user_id: str):
    """Delete a user from the database."""
    if not ObjectId.is_valid(user_id):
        return False
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0


async def get_user_preferences(google_id: str):
    """Retrieve only user preferences."""
    user = await db.users.find_one({"google_id": google_id}, {"preferences": 1, "_id": 0})
    return user.get("preferences", {}) if user else None


async def update_user_preferences(google_id: str, preferences: dict):
    """Update user preferences."""
    result = await db.users.update_one(
        {"google_id": google_id},
        {"$set": {"preferences": preferences}}
    )
    return result.modified_count > 0