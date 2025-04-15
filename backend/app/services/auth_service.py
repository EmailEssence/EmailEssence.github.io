import os
import logging  
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from app.models import UserSchema
from google.oauth2.credentials import Credentials
from starlette.concurrency import run_in_threadpool
from app.utils.config import get_settings
from app.services.database import TokenRepository, get_token_repository

settings = get_settings()

SCOPES = [
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid',
    'https://www.googleapis.com/auth/userinfo.profile'
]

logger = logging.getLogger(__name__)

class TokenData(BaseModel):
    token: str
    refresh_token: Optional[str] = None
    token_uri: str
    client_id: str
    client_secret: str
    scopes: list

class AuthService:
    """
    Service for handling authentication and authorization.
    
    This class provides methods for OAuth2 flow, token management,
    and user authentication.
    """
    
    def __init__(self, token_repo: TokenRepository = Depends(get_token_repository)):
        """Initialize the auth service with required configuration"""
        self.token_repo = token_repo

    def create_authorization_url(self, custom_state=None) -> Dict[str, str]:
        """Generates Google OAuth2 authorization URL."""
        logger.debug("Generating Google OAuth2 authorization URL...")

        client_id = settings.google_client_id
        client_secret = settings.google_client_secret

        if not client_id or not client_secret:
            logger.error("Google API credentials missing.")
            raise HTTPException(status_code=500, detail="Google API credentials not found in settings.")

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

        logger.debug(f"Using redirect URI: {flow.redirect_uri}")

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

    async def get_tokens_from_code(self, code: str, user_email: str) -> Dict[str, str]:
        """Exchanges auth code for tokens and stores them in the DB."""
        logger.info(f"Exchanging authorization code for tokens... User: {user_email}")

        try:
            client_id = settings.google_client_id
            client_secret = settings.google_client_secret
            
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
            flow.fetch_token(code=code)
            credentials = flow.credentials

            logger.info("Token successfully fetched from Google.")

            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
 
            if user_email:
                logger.debug(f"Storing tokens in DB for {user_email}...")
                await self.token_repo.update_one(
                    {"user_email": user_email},
                    token_data,
                    upsert=True
                )
                logger.info("Tokens successfully stored.")

            return token_data

        except Exception as e:
            logger.exception("Auth code exchange failed.")
            raise HTTPException(status_code=400, detail=f"Auth code exchange failed: {str(e)}")

    async def get_credentials(self, user_email: str) -> Optional[TokenData]:
        """Retrieves credentials from DB, refreshing if needed."""
        logger.debug(f"Retrieving credentials for user: {user_email}")

        token_record = await self.token_repo.find_one({"user_email": user_email})

        if not token_record:
            logger.warning("No credentials found in database.")
            raise HTTPException(status_code=401, detail="No credentials found. Please authenticate.")

        credentials = TokenData(**token_record)
        logger.info(f"Token found for user: {user_email}")

        if not credentials.token:
            logger.warning("Stored token is invalid. Re-authentication required")
            raise HTTPException(status_code=401, detail="Invalid token stored.")

        if credentials.refresh_token:
            try:
                logger.debug("Refreshing expired token...")
                flow = Flow.from_client_config({
                    "web": {
                        "client_id": credentials.client_id,
                        "client_secret": credentials.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.get_redirect_uri()]
                    }
                }, SCOPES)
                flow.credentials.refresh(Request())

                await self.token_repo.update_one(
                    {"user_email": user_email},
                    {"token": flow.credentials.token}
                )
                logger.info("Token refreshed and updated in DB.")
                return flow.credentials.token

            except Exception as e:
                logger.exception("Token refresh failed.")
                raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")

        return credentials.token

    def get_redirect_uri(self):
        """Returns the OAuth redirect URI."""
        logger.debug("Retrieving redirect URI...")

        if callback_url := settings.oauth_callback_url:
            logger.debug(f"Using env-specified callback URL: {callback_url}")
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
        logger.debug("Validating access token and retrieving user info...")

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

            if not user_info or not user_info.get('email'):
                logger.error("Unable to retrieve user email from token.")
                raise ValueError("Unable to retrieve user email from token")

            logger.info(f"User info retrieved for: {user_info.get('email')}")

            return {
                'user_info': user_info,
                'credentials': credentials,
                'email': user_info.get('email')
            }

        except Exception as e:
            logger.exception("Token validation failed.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")
