"""
Common dependencies for Email Essence FastAPI application.

This module centralizes shared dependencies including authentication schemes,
logging configuration, and common helper functions used across routers and services.
"""

import logging
from typing import Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Internal imports
from app.models.user_models import UserSchema
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.database.factories import get_auth_service, get_user_service
from app.utils.helpers import get_logger, configure_module_logging, standardize_error_response, log_operation

# -------------------------------------------------------------------------
# Authentication Dependencies
# -------------------------------------------------------------------------

# Centralized OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token", 
    description="Enter the token you received from the login flow (without Bearer prefix)"
)

async def get_current_user_email(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> str:
    """
    Dependency to extract user email from valid token.
    
    Args:
        token: JWT token from OAuth2 authentication
        auth_service: Auth service instance
        
    Returns:
        str: User's email address
        
    Raises:
        HTTPException: 401 error if token is invalid
    """
    try:
        user_data = await auth_service.get_credentials_from_token(token)
        return user_data['email']
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
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
    try:
        user_data = await auth_service.get_credentials_from_token(token)
        return user_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication: {str(e)}"
        )

async def get_current_user(
    user_data: Dict[str, Any] = Depends(get_current_user_info),
    user_service: UserService = Depends(get_user_service)
) -> UserSchema:
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
    try:
        user_info = user_data['user_info']
        user_email = user_info.get('email')
        google_id = user_info.get('google_id')
        
        # Try to get existing user
        user = await user_service.get_user_by_email(user_email)
        
        # If user doesn't exist, create new user
        if not user:
            user = await user_service.create_user({
                "email": user_email,
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", ""),
                "google_id": google_id
            })
        else:
            # Update google_id if it's missing
            user_dict = user.model_dump()
            if not user_dict.get('google_id'):
                await user_service.update_user(user_dict['_id'], {"google_id": google_id})
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )

 