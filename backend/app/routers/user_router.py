"""
User router for Email Essence.

This module handles user profile management, preferences, and user-related operations.
It provides endpoints for retrieving and updating user information and preferences.
"""

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
    """Print debug messages with a consistent format"""
    print(f"[DEBUG] {message}")

async def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """
    Validates token and returns user information.
    
    Args:
        token: JWT token from OAuth2 authentication
        
    Returns:
        dict: User information and credentials
        
    Raises:
        HTTPException: 401 error if token is invalid
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

@router.get(
    "/me", 
    response_model=UserSchema,
    summary="Get current user profile",
    description="Retrieves the authenticated user's profile information or creates a new user record if one doesn't exist"
)
async def get_current_user(user_data: dict = Depends(get_current_user_info)):
    """
    Retrieve user details or create user if they don't exist.
    
    Args:
        user_data: User information and credentials from token validation
        
    Returns:
        UserSchema: User profile information
        
    Raises:
        HTTPException: If user retrieval fails
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

@router.get(
    "/preferences",
    summary="Get user preferences",
    description="Retrieves the authenticated user's preference settings"
)
async def get_user_preferences(user_data: dict = Depends(get_current_user_info)):
    """
    Retrieves the user's preferences from their profile.
    
    Args:
        user_data: User information from token validation
        
    Returns:
        dict: User preference settings
        
    Raises:
        HTTPException: If preferences cannot be retrieved
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

@router.put(
    "/preferences",
    summary="Update user preferences",
    description="Updates the authenticated user's preference settings"
)
async def update_preferences(
    preferences: dict, 
    user_data: dict = Depends(get_current_user_info)
):
    """
    Updates the user's preference settings.
    
    Args:
        preferences: Dictionary of preference settings to update
        user_data: User information from token validation
        
    Returns:
        dict: Updated user preferences
        
    Raises:
        HTTPException: If preference update fails
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

@router.get(
    "/{user_id}",
    response_model=UserSchema,
    summary="Get user by ID",
    description="Retrieves user information by user ID"
)
async def get_user(user_id: str):
    """
    Retrieves a user by their ID.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        UserSchema: User profile information
        
    Raises:
        HTTPException: If user not found
    """
    debug(f"Retrieving user with ID: {user_id}")
    
    user = await get_user_by_id(user_id)
    if not user:
        debug(f"[ERROR] User not found: {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    debug(f"User retrieved successfully: {user.get('email', 'Unknown')}")
    return user

@router.put(
    "/{user_id}",
    response_model=UserSchema,
    summary="Update user",
    description="Updates user information by user ID"
)
async def update_user_info(user_id: str, user_data: dict):
    """
    Updates a user's information.
    
    Args:
        user_id: Unique identifier for the user
        user_data: User information to update
        
    Returns:
        UserSchema: Updated user profile
        
    Raises:
        HTTPException: If user update fails
    """
    debug(f"Updating user: {user_id}")
    
    updated_user = await update_user(user_id, user_data)
    if not updated_user:
        debug(f"[ERROR] User update failed: {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or update failed")
    
    debug(f"User updated successfully: {user_id}")
    return updated_user

@router.delete(
    "/{user_id}",
    summary="Delete user",
    description="Deletes a user account by user ID",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user_info(user_id: str):
    """
    Deletes a user from the system.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        None
        
    Raises:
        HTTPException: If user deletion fails
    """
    debug(f"Deleting user: {user_id}")
    
    success = await delete_user(user_id)
    if not success:
        debug(f"[ERROR] User delete failed: {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or delete failed")
    
    debug(f"User deleted successfully: {user_id}")
    return JSONResponse(content={"message": "User deleted successfully"}, status_code=status.HTTP_200_OK)
    