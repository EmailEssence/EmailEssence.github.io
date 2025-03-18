from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.concurrency import run_in_threadpool

from app.models import UserSchema
from app.services.auth_service import get_tokens_from_code, get_credentials, get_credentials_from_token
from app.services.user_service import get_or_create_user, get_user_by_id, update_user, delete_user
from database import db

router = APIRouter()

# OAuth authentication scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", description="Enter the token you received from the login flow (without Bearer prefix)")

# Debugging helper function
def debug(message: str):
    print(f"[DEBUG] {message}")

async def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """
    Validates token and returns user information.
    """
    debug(f"Validating token for user authentication...")
    
    try:
        user_data = await get_credentials_from_token(token)
        debug(f"User authenticated successfully: {user_data.get('user_info', {}).get('email', 'Unknown')}")
        return user_data
    except Exception as e:
        debug(f"[ERROR] Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication: {str(e)}"
        )

@router.get("/me")
async def get_current_user(user_data: dict = Depends(get_current_user_info)):
    """
    Retrieve user details or create user if they don't exist.
    """
    debug("Retrieving current user...")
    
    try:
        user_info = user_data['user_info']
        credentials = user_data['credentials']
        
        debug(f"Fetching user from database or creating new: {user_info.get('email', 'Unknown')}")
        user = await get_or_create_user(user_info, credentials)
        
        
        debug(f"User retrieval successful: {user.get('email', 'Unknown')}")
        return user
    except Exception as e:
        debug(f"[ERROR] Failed to retrieve user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )

@router.get("/{user_id}")
async def get_user(user_id: str):
    """
    Retrieve a user by ID.
    """
    debug(f"Retrieving user with ID: {user_id}")
    
    user = await get_user_by_id(user_id)
    if not user:
        debug(f"[ERROR] User not found: {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    debug(f"User retrieved successfully: {user.get('email', 'Unknown')}")
    return user

@router.put("/{user_id}")
async def update_user_info(user_id: str, user_data: dict):
    """
    Update user details.
    """
    debug(f"Updating user: {user_id}")
    
    updated_user = await update_user(user_id, user_data)
    if not updated_user:
        debug(f"[ERROR] User update failed: {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or update failed")
    
    debug(f"User updated successfully: {user_id}")
    return updated_user

@router.delete("/{user_id}")
async def delete_user_info(user_id: str):
    """
    Delete a user by ID.
    """
    debug(f"Deleting user: {user_id}")
    
    success = await delete_user(user_id)
    if not success:
        debug(f"[ERROR] User delete failed: {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or delete failed")
    
    debug(f"User deleted successfully: {user_id}")
    return JSONResponse(content={"message": "User deleted successfully"}, status_code=status.HTTP_200_OK)

@router.get("/preferences")
async def get_user_preferences(user_data: dict = Depends(get_current_user_info)):
    """
    Retrieve user preferences without exposing the full user model.
    """
    debug("Retrieving user preferences...")
    
    try:
        user_info = user_data['user_info']
        
        
        debug(f"Fetching preferences for user: {user_info.get('email', 'Unknown')}")
        user = await db.users.find_one({"google_id": user_info["id"]}, {"preferences": 1, "_id": 0})

        if not user:
            debug(f"[ERROR] User not found while retrieving preferences: {user_info.get('email', 'Unknown')}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        debug(f"Preferences retrieved successfully for user: {user_info.get('email', 'Unknown')}")
        return {"preferences": user.get("preferences", {})}
    except Exception as e:
        debug(f"[ERROR] Failed to retrieve user preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user preferences: {str(e)}"
        )

@router.put("/preferences")
async def update_preferences(
    preferences: dict, 
    user_data: dict = Depends(get_current_user_info)
):
    """
    Allows users to update their preferences.
    """
    
    debug("Updating user preferences...")
    
    try:
        user_info = user_data['user_info']
        
        debug(f"Updating preferences for user: {user_info.get('email', 'Unknown')}")
        await db.users.update_one(
            {"google_id": user_info["id"]},
            {"$set": {"preferences": preferences}}
        )
        
        debug(f"Preferences updated successfully for user: {user_info.get('email', 'Unknown')}")
        return JSONResponse(content={"message": "Preferences updated successfully"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        debug(f"[ERROR] Failed to update preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )
    