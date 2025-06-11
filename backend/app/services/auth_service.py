"""
Service for handling authentication and authorization.

This module provides services for OAuth2 authentication, token management,
and user authentication with Google.
"""

# Standard library imports
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Third-party imports
from fastapi import HTTPException, status
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from starlette.concurrency import run_in_threadpool

# Internal imports
from app.utils.helpers import get_logger, log_operation, standardize_error_response
from app.models import AuthState, TokenData, UserSchema
from app.services.database import (
    TokenRepository,
    UserRepository,
    get_token_repository,
    get_user_repository,
)
from app.services.user_service import UserService
from app.utils.config import Settings, get_settings

# -------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------

logger = get_logger(__name__, 'service')
settings = get_settings()

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid',
    'https://mail.google.com/'
]

class AuthService:
    """
    Service for handling authentication and authorization.
    
    This class provides methods for OAuth2 flow, token management,
    and user authentication.
    """
    
    def __init__(
        self,
        token_repository: TokenRepository = None,
        user_repository: UserRepository = None,
        user_service: UserService = None
    ):
        """
        Initialize the auth service.
        
        Args:
            token_repository: Token repository instance
            user_repository: User repository instance
            user_service: User service instance
        """
        self.token_repository = token_repository or get_token_repository()
        self.user_repository = user_repository or get_user_repository()
        self.user_service = user_service or UserService(self.user_repository)

    async def verify_user_access(
        self,
        user_id: str,
        current_user_data: dict,
        user_service: UserService
    ) -> bool:
        """
        Verifies if the current user has access to the requested user's data.
        
        Args:
            user_id: ID of the user being accessed
            current_user_data: Data of the currently authenticated user
            user_service: User service instance
            
        Returns:
            bool: True if access is granted
            
        Raises:
            HTTPException: 403 if access is denied
        """
        log_operation(logger, 'debug', f"Verifying user access for user ID: {user_id}")
        
        try:
            # Get the current user's email from the token data
            token_record = await self.get_token_record(current_user_data['google_id'])
            if not token_record:
                log_operation(logger, 'warning', f"No token record found for user: {current_user_data['google_id']}")
                raise standardize_error_response(
                    Exception("No valid token record found"), 
                    "verify user access", 
                    current_user_data['google_id']
                )
            
            current_user = await user_service.get_user(current_user_data['user_info']['id'])
            if not current_user:
                raise standardize_error_response(
                    Exception("Current user not found"), 
                    "verify user access", 
                    current_user_data['google_id']
                )
                
            # Allow access if:
            # 1. User is accessing their own data
            # 2. User has admin privileges
            if current_user['google_id'] == user_id or current_user.get('is_admin', False):
                log_operation(logger, 'debug', f"Access granted for user ID: {user_id}")
                return True
                
            log_operation(logger, 'debug', f"Access denied for user ID: {user_id}")
            raise standardize_error_response(
                Exception("You do not have permission to access this resource"), 
                "verify user access", 
                user_id
            )
        except Exception as e:
            raise standardize_error_response(e, "verify user access", user_id)

    def create_authorization_url(self, custom_state=None) -> Dict[str, str]:
        """Generates Google OAuth2 authorization URL."""
        log_operation(logger, 'debug', "Generating Google OAuth2 authorization URL...")

        client_id = settings.google_client_id
        client_secret = settings.google_client_secret

        if not client_id or not client_secret:
            raise standardize_error_response(
                Exception("Google API credentials missing"), 
                "create authorization URL"
            )

        client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.get_redirect_uri()]
            }
        }

        flow = Flow.from_client_config(client_config, SCOPES)
        flow.redirect_uri = self.get_redirect_uri()

        log_operation(logger, 'debug', f"Using redirect URI: {flow.redirect_uri}")

        if custom_state:
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=custom_state
            )
        else:
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            custom_state = state

        return {"authorization_url": authorization_url, "state": custom_state}

    async def get_tokens_from_code(self, code: str, email: str) -> TokenData:
        """
        Get tokens from authorization code.
        
        Args:
            code: Authorization code
            email: User's email
            
        Returns:
            TokenData: Token data
        """
        try:
            # Create flow instance
            client_config = {
                "web": {
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.get_redirect_uri()]
                }
            }
            
            flow = Flow.from_client_config(client_config, SCOPES)
            flow.redirect_uri = self.get_redirect_uri()
            
            # Exchange code for tokens
            flow.fetch_token(code=code)
            
            # Get user info to get google_id
            service = await run_in_threadpool(lambda: 
                build('oauth2', 'v2', credentials=flow.credentials)
            )
            
            user_info = await run_in_threadpool(lambda: 
                service.userinfo().get().execute()
            )
            
            if not user_info or not user_info.get('id'):
                raise ValueError("Unable to retrieve user info from token")
            
            # Create token data
            token_data = {
                "google_id": user_info['id'],
                "token": flow.credentials.token,
                "refresh_token": flow.credentials.refresh_token,
                "token_uri": flow.credentials.token_uri,
                "client_id": flow.credentials.client_id,
                "client_secret": flow.credentials.client_secret,
                "scopes": flow.credentials.scopes
            }
            
            # Create TokenData instance
            token = TokenData(**token_data)
            
            try:
                # Try to insert new token
                await self.token_repository.insert_one(token)
            except Exception as e:
                if "duplicate key error" in str(e):
                    # If token exists, update it
                    await self.token_repository.update_by_google_id(user_info['id'], token_data)
                else:
                    raise
            
            logger.info(f"Successfully stored tokens for user: {email}")
            return token
            
        except Exception as e:
            raise standardize_error_response(e, "get tokens from code", email)

    async def get_current_user(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get current user by email.
        
        Args:
            email: User's email address
            
        Returns:
            Optional[Dict[str, Any]]: User data if found, None otherwise
        """
        try:
            user = await self.user_repository.find_by_email(email)
            if not user:
                # Create new user if not found
                user = await self.user_repository.insert_one(UserSchema(
                    email=email,
                    name="",
                    picture="",
                    google_id=""
                ))
            return user.model_dump()
        except Exception as e:
            raise standardize_error_response(e, "get current user", email)

    async def get_token_data(self, google_id: str) -> Optional[TokenData]:
        """
        Get token data for a user.
        
        Args:
            google_id: User's Google ID
            
        Returns:
            Optional[TokenData]: Token data if found, None otherwise
        """
        try:
            return await self.token_repository.find_by_google_id(google_id)
        except Exception as e:
            raise standardize_error_response(e, "get token data", google_id)

    def get_redirect_uri(self):
        """Returns the OAuth redirect URI."""
        log_operation(logger, 'debug', "Retrieving redirect URI...")

        if callback_url := settings.oauth_callback_url:
            log_operation(logger, 'debug', f"Using env-specified callback URL: {callback_url}")
            return callback_url

        environment = settings.environment
        base_url = settings.backend_base_url
        if base_url:
            return f"{base_url.rstrip('/')}/auth/callback"
        elif environment == 'development':
            return 'http://localhost:8000/auth/callback'
        else:
            return 'https://ee-backend-w86t.onrender.com/auth/callback'

    async def get_credentials_from_token(self, token: str):
        """
        Validates a token and returns user information from Google.
        Used for authenticating API requests.
        """
        log_operation(logger, 'debug', "Validating access token and retrieving user info...")

        try:
            # First try to validate the token directly
            try:
                credentials = Credentials(
                    token=token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=settings.google_client_id,
                    client_secret=settings.google_client_secret
                )

                service = await run_in_threadpool(lambda: 
                    build('oauth2', 'v2', credentials=credentials)
                )
                
                user_info = await run_in_threadpool(lambda: 
                    service.userinfo().get().execute()
                )
            except Exception as e:
                log_operation(logger, 'debug', f"Initial token validation failed, attempting refresh: {e}")
                # If token validation fails, try to get a new token using refresh token
                token_record = await self.token_repository.find_by_token(token)
                if not token_record or not token_record.refresh_token:
                    raise standardize_error_response(
                        Exception("Invalid or expired token"), 
                        "get credentials from token"
                    )
                
                # Create credentials with refresh token
                credentials = Credentials(
                    None,
                    refresh_token=token_record.refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=settings.google_client_id,
                    client_secret=settings.google_client_secret
                )
                
                # Refresh the token
                credentials.refresh(Request())
                
                # Update the token in the database
                await self.token_repository.update_tokens(
                    token_record.email,
                    credentials.token,
                    credentials.refresh_token
                )
                
                # Build service with new credentials
                service = await run_in_threadpool(lambda: 
                    build('oauth2', 'v2', credentials=credentials)
                )
                
                user_info = await run_in_threadpool(lambda: 
                    service.userinfo().get().execute()
                )

            if not user_info or not user_info.get('email'):
                log_operation(logger, 'error', "Unable to retrieve user email from token.")
                raise ValueError("Unable to retrieve user email from token")

            # Add google_id to user_info
            user_info['google_id'] = user_info.get('id')
            
            log_operation(logger, 'info', f"User info retrieved for: {user_info.get('email')}")

            return {
                'user_info': user_info,
                'credentials': credentials,
                'email': user_info.get('email')
            }

        except Exception as e:
            raise standardize_error_response(e, "get credentials from token")

    async def get_token_record(self, google_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the complete token record from the database.
        
        Args:
            google_id: User's Google ID
            
        Returns:
            Optional[Dict[str, Any]]: Complete token record if found, None otherwise
        """
        try:
            log_operation(logger, 'debug', f"Getting token record for google_id: {google_id}")
            token_data = await self.token_repository.find_by_google_id(google_id)
            if not token_data:
                log_operation(logger, 'warning', f"No token record found for google_id: {google_id}")
                return None
            log_operation(logger, 'info', f"Found token record for google_id: {google_id}")
            # Convert TokenData to dict if it's a model instance
            if hasattr(token_data, 'model_dump'):
                return token_data.model_dump()
            return token_data
        except Exception as e:
            raise standardize_error_response(e, "get token record", google_id)
