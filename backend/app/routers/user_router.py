"""
User router for Email Essence.

This module handles user profile management, preferences, and user-related operations.
It provides endpoints for retrieving and updating user information and preferences.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from functools import lru_cache
from typing import Optional, Dict, Any

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from starlette.concurrency import run_in_threadpool

from app.models import UserSchema, PreferencesSchema
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.database.factories import get_user_service, get_auth_service

router = APIRouter()

# OAuth authentication scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", description="Enter the token you received from the login flow (without Bearer prefix)")

# Debugging helper function
def debug(message: str):
    """Print debug messages with a consistent format"""
    print(f"[DEBUG] {message}")

async def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Validates token and returns user information.
    
    Args:
        token: JWT token from OAuth2 authentication
        auth_service: Auth service instance
        
    Returns:
        dict: User information and credentials
        
    Raises:
        HTTPException: 401 error if token is invalid
    """
    debug(f"Validating token for user authentication...")
    
    try:
        user_data = await auth_service.get_credentials_from_token(token)
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
async def get_current_user(
    user_data: dict = Depends(get_current_user_info),
    user_service: UserService = Depends(get_user_service)
):
    """
    Retrieve user details or create user if they don't exist.
    
    Args:
        user_data: User information and credentials from token validation
        user_service: User service instance
        
    Returns:
        UserSchema: User profile information
        
    Raises:
        HTTPException: If user retrieval fails
    """
    debug("Retrieving current user...")
    
    try:
        user_info = user_data['user_info']
        user_email = user_info.get('email')
        google_id = user_info.get('google_id')
        
        debug(f"Fetching user from database or creating new: {user_email}")
        
        # Try to get existing user
        user = await user_service.get_user_by_email(user_email)
        
        # If user doesn't exist, create new user
        if not user:
            debug(f"Creating new user: {user_email}")
            user = await user_service.create_user({
                "email": user_email,
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", ""),
                "google_id": google_id
            })
        else:
            debug(f"Found existing user: {user_email}")
            # Convert UserSchema to dict for checking google_id
            user_dict = user.dict()
            # Update google_id if it's missing
            if not user_dict.get('google_id'):
                debug(f"Updating missing google_id for user: {user_email}")
                await user_service.update_user(user_dict['_id'], {"google_id": google_id})
        
        debug(f"User retrieval successful: {user_email}")
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
async def get_user_preferences(
    user_data: dict = Depends(get_current_user_info),
    user_service: UserService = Depends(get_user_service)
):
    """
    Retrieves the user's preferences from their profile.
    
    Args:
        user_data: User information from token validation
        user_service: User service instance
        
    Returns:
        dict: User preference settings
        
    Raises:
        HTTPException: If preferences cannot be retrieved
    """
    debug("Retrieving user preferences...")
    
    try:
        user_info = user_data['user_info']
        user_email = user_info.get('email')
        
        debug(f"Fetching preferences for user: {user_email}")
        
        # Get user first to ensure they exist
        user = await user_service.get_user_by_email(user_email)
        if not user:
            debug(f"User not found: {user_email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        preferences = user.preferences.dict()
        debug(f"Preferences retrieved successfully for user: {user_email}")
        return {"preferences": preferences}
    except HTTPException:
        raise
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
    preferences: PreferencesSchema,
    user_data: dict = Depends(get_current_user_info),
    user_service: UserService = Depends(get_user_service)
):
    """
    Updates the user's preference settings.
    
    Args:
        preferences: Preference settings to update
        user_data: User information from token validation
        user_service: User service instance
        
    Returns:
        dict: Updated user preferences
        
    Raises:
        HTTPException: If preference update fails
    """
    debug("Updating user preferences...")
    
    try:
        user_info = user_data['user_info']
        user_email = user_info.get('email')
        
        debug(f"Updating preferences for user: {user_email}")
        
        # Get user first to ensure they exist
        user = await user_service.get_user_by_email(user_email)
        if not user:
            debug(f"User not found: {user_email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        debug(f"Found user with ID: {user.google_id}")
        debug(f"Current user data: {user.dict()}")
            
        # Create update data with existing user fields and new preferences
        update_data = {
            "google_id": user.google_id,
            "email": user.email,
            "name": user.name,
            "oauth": user.oauth.dict() if hasattr(user, 'oauth') else {},
            "preferences": preferences.dict()
        }
        
        debug(f"Update data: {update_data}")
        
        # Update user with new preferences
        try:
            updated_user = await user_service.update_user(
                user.google_id,
                update_data
            )
        except Exception as e:
            debug(f"Error updating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user: {str(e)}"
            )
        
        if not updated_user:
            debug("Update returned None")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preferences"
            )
        
        debug(f"Updated user data: {updated_user.dict()}")
        debug(f"Preferences updated successfully for user: {user_email}")
        return {"preferences": updated_user.preferences.dict()}
    except HTTPException:
        raise
    except Exception as e:
        debug(f"[ERROR] Failed to update preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserSchema:
    """
    Get a user by ID.
    
    Args:
        user_id: The ID of the user to retrieve
        user_service: Injected UserService instance
        auth_service: Injected AuthService instance
        
    Returns:
        UserSchema: The requested user
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/email/{email}", response_model=UserSchema)
async def get_user_by_email(
    email: str,
    user_service: UserService = Depends(get_user_service)
) -> UserSchema:
    """
    Get a user by email.
    
    Args:
        email: The email of the user to retrieve
        user_service: Injected UserService instance
        
    Returns:
        UserSchema: The requested user
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/", response_model=UserSchema)
async def create_user(
    user_data: UserSchema,
    user_service: UserService = Depends(get_user_service)
) -> UserSchema:
    """
    Create a new user.
    
    Args:
        user_data: The user data to create
        user_service: Injected UserService instance
        
    Returns:
        UserSchema: The created user
    """
    return await user_service.create_user(user_data)

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    user_data: UserSchema,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserSchema:
    """
    Update a user.
    
    Args:
        user_id: The ID of the user to update
        user_data: The updated user data
        user_service: Injected UserService instance
        auth_service: Injected AuthService instance
        
    Returns:
        UserSchema: The updated user
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = await user_service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """
    Delete a user.
    
    Args:
        user_id: The ID of the user to delete
        user_service: Injected UserService instance
        auth_service: Injected AuthService instance
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 404 if user not found
    """
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}
    