from database import db
from app.models.user_model import UserSchema
from bson import ObjectId

async def get_or_create_user(user_info, credentials):
    """Finds or creates a user in the database based on Google OAuth data."""
    google_id = user_info["id"]  # Unique Google ID
    existing_user = await db.users.find_one({"google_id": google_id})

    if existing_user:
        # Convert _id to string for JSON serialization
        existing_user["_id"] = str(existing_user["_id"])
        return existing_user

    # Create new user record
    new_user = UserSchema(
        google_id=google_id,
        email=user_info["email"],
        name=user_info["name"],
        picture=user_info.get("picture"),
        locale=user_info.get("locale"),
        oauth={
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        },
        preferences={},
    )

    # Insert into MongoDB
    inserted_id = await db.users.insert_one(new_user.model_dump())
    new_user_dict = new_user.model_dump()
    new_user_dict["_id"] = str(inserted_id.inserted_id)  # Convert ObjectId to string
    return new_user_dict