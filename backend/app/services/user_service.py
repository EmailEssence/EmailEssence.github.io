from database import db
from app.models.user_model import UserSchema
from bson import ObjectId

async def get_or_create_user(user_data):
    """Finds or creates a user in the database based on Google OAuth data."""
    google_id = user_data["sub"]  # Unique Google ID
    existing_user = await db.users.find_one({"google_id": google_id})

    if existing_user:
        return existing_user  # Return existing user

    # Create new user record
    new_user = UserSchema(
        google_id=google_id,
        email=user_data["email"],
        name=user_data["name"],
        picture=user_data.get("picture"),
        locale=user_data.get("locale"),
        oauth={
            "access_token": user_data["access_token"],
            "refresh_token": user_data.get("refresh_token", ""),
        },
        preferences={},
    )

    # Insert into MongoDB
    inserted_id = await db.users.insert_one(new_user.dict(by_alias=True))
    return await db.users.find_one({"_id": inserted_id.inserted_id})