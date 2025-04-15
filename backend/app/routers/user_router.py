"""
User router for Email Essence.

This module handles user profile management, preferences, and user-related operations.
It provides endpoints for retrieving and updating user information and preferences.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from functools import lru_cache

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from starlette.concurrency import run_in_threadpool

from app.models import UserSchema
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()

# -- Service Dependencies --

@lru_cache()
def get_auth_service() -> AuthService:
    """
    Factory function that returns an AuthService instance.
    Using lru_cache for efficiency so we don't create a new instance for every request.
    """
    return AuthService()

@lru_cache()
def get_user_service() -> UserService:
    """
    Factory function that returns a UserService instance.
    Using lru_cache for efficiency so we don't create a new instance for every request.
    """
    return UserService()

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
        credentials = user_data['credentials']
        
        debug(f"Fetching user from database or creating new: {user_info.get('email', 'Unknown')}")
        user = await user_service.get_or_create_user(user_info, credentials)
        
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
        
        debug(f"Fetching preferences for user: {user_info.get('email', 'Unknown')}")
        preferences = await user_service.get_user_preferences(user_info["id"])

        if not preferences:
            debug(f"[ERROR] User not found while retrieving preferences: {user_info.get('email', 'Unknown')}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        debug(f"Preferences retrieved successfully for user: {user_info.get('email', 'Unknown')}")
        return {"preferences": preferences}
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
    user_data: dict = Depends(get_current_user_info),
    user_service: UserService = Depends(get_user_service)
):
    """
    Updates the user's preference settings.
    
    Args:
        preferences: Dictionary of preference settings to update
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
        
        debug(f"Updating preferences for user: {user_info.get('email', 'Unknown')}")
        success = await user_service.update_user_preferences(user_info["id"], preferences)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
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
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Retrieves a user by their ID.
    
    Args:
        user_id: Unique identifier for the user
        user_service: User service instance
        
    Returns:
        UserSchema: User profile information
        
    Raises:
        HTTPException: If user not found
    """
    debug(f"Retrieving user with ID: {user_id}")
    
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except Exception as e:
        debug(f"[ERROR] Failed to retrieve user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )

@router.put(
    "/{user_id}",
    response_model=UserSchema,
    summary="Update user",
    description="Updates user information by user ID"
)
async def update_user_info(
    user_id: str, 
    user_data: dict,
    user_service: UserService = Depends(get_user_service)
):
    """
    Updates a user's information.
    
    Args:
        user_id: Unique identifier for the user
        user_data: Updated user information
        user_service: User service instance
        
    Returns:
        UserSchema: Updated user profile information
        
    Raises:
        HTTPException: If update fails
    """
    debug(f"Updating user with ID: {user_id}")
    
    try:
        updated_user = await user_service.update_user(user_id, user_data)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated_user
    except Exception as e:
        debug(f"[ERROR] Failed to update user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete(
    "/{user_id}",
    summary="Delete user",
    description="Deletes a user account by user ID",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user_info(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Deletes a user account.
    
    Args:
        user_id: Unique identifier for the user
        user_service: User service instance
        
    Raises:
        HTTPException: If deletion fails
    """
    debug(f"Deleting user with ID: {user_id}")
    
    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        debug(f"[ERROR] Failed to delete user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )
    