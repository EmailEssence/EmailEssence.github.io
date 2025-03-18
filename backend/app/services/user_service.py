from database import db
from app.models.user_model import UserSchema
from bson import ObjectId

# Debugging helper function
def debug(message: str):
    print(f"[DEBUG] {message}")

async def get_or_create_user(user_info, credentials=None):
    """Finds or creates a user in the database based on Google OAuth data."""
    google_id = user_info["id"]  # Unique Google ID
    debug(f"Checking if user with Google ID {google_id} exists...")

    existing_user = await db.users.find_one({"google_id": google_id})

    if existing_user:
        # Convert _id to string for JSON serialization
        existing_user["_id"] = str(existing_user["_id"])
        debug(f"User found: {existing_user['email']}")
        return existing_user

    debug(f"User not found. Creating new user with email: {user_info['email']}")

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
        debug(f"OAuth credentials included for {user_info['email']}.")

    # Create new user record
    new_user = UserSchema(
        google_id=google_id,
        email=user_info["email"],
        name=user_info.get("name", user_info.get("email").split("@")[0]),
        oauth=oauth_data
    )

    # Insert into MongoDB
    inserted_id = await db.users.insert_one(new_user.model_dump())
    debug(f"New user inserted with ID: {inserted_id.inserted_id}")

    new_user_dict = new_user.model_dump()
    new_user_dict["_id"] = str(inserted_id.inserted_id)  # Convert ObjectId to string
    return new_user_dict

async def get_user_by_id(user_id: str):
    """Retrieve user by ID."""
    debug(f"Fetching user with ID: {user_id}")

    if not ObjectId.is_valid(user_id):
        debug("[ERROR] Invalid ObjectId format.")
        return None
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if user:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string for frontend compatibility
        debug(f"User retrieved: {user.get('email', 'Unknown')}")
    else:
        debug("[ERROR] User not found.")
    
    return user

async def update_user(user_id: str, user_data: dict):
    """Update a user's information."""
    debug(f"Updating user with ID: {user_id}")

    if not ObjectId.is_valid(user_id):
        debug("[ERROR] Invalid ObjectId format.")
        return None
    
    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
    
    if result.modified_count == 0:
        debug("[ERROR] No modifications were made.")
        return None  # No update performed
    
    debug(f"User {user_id} updated successfully.")
    return await get_user_by_id(user_id)

async def delete_user(user_id: str):
    """Delete a user from the database."""
    debug(f"Attempting to delete user with ID: {user_id}")

    if not ObjectId.is_valid(user_id):
        debug("[ERROR] Invalid ObjectId format.")
        return False

    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0


async def get_user_preferences(google_id: str):
    """Retrieve only user preferences."""
    debug(f"Fetching preferences for Google ID: {google_id}")
    user = await db.users.find_one({"google_id": google_id}, {"preferences": 1, "_id": 0})
    return user.get("preferences", {}) if user else None
    


async def update_user_preferences(google_id: str, preferences: dict):
    """Update user preferences."""
    debug(f"Updating preferences for Google ID: {google_id}")

    result = await db.users.update_one(
        {"google_id": google_id},
        {"$set": {"preferences": preferences}}
    )
    
    return result.modified_count > 0
