import os
import pickle
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, Dict
from app.models import UserSchema


load_dotenv()

SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/userinfo.email', 'openid', 'https://www.googleapis.com/auth/userinfo.profile']

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list = []
    
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user."}
)

def create_authorization_url() -> Dict[str, str]:
    # Load client ID and client secret from environment variables
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Google API credentials not found in environment variables.")

    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [get_redirect_uri()]
        }
    }

    flow = Flow.from_client_config(client_config, SCOPES)
    flow.redirect_uri = get_redirect_uri()

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    return {"authorization_url": authorization_url, "state": state}

def get_tokens_from_code(code: str) -> Dict[str, str]:
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [get_redirect_uri()]
        }
    }

    flow = Flow.from_client_config(client_config, SCOPES)
    flow.redirect_uri = get_redirect_uri()

    flow.fetch_token(code=code)
    credentials = flow.credentials

    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_redirect_uri():
    """
    Returns the backend callback URL for OAuth.
    Can be overridden with OAUTH_CALLBACK_URL environment variable.
    """
    if callback_url := os.getenv('OAUTH_CALLBACK_URL'):
        return callback_url

    environment = os.getenv('ENVIRONMENT', 'development')
    base_url = os.getenv('BACKEND_BASE_URL')

    if base_url:
        return f"{base_url.rstrip('/')}/auth/callback"
    elif environment == 'development':
        return 'http://localhost:8000/auth/callback'
    else:
        return 'https://ee-backend-w86t.onrender.com/auth/callback'

def get_credentials():
    """
    Retrieves or creates Google OAuth2 credentials
    """
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise Exception("Google API credentials not found in environment variables.")
        
    # Try to load existing credentials
    creds = None
    token_path = 'token.pickle'
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials available, create new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Create new flow if we can't refresh
            client_config = {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [get_redirect_uri()]
                }
            }
            flow = Flow.from_client_config(client_config, SCOPES)
            flow.redirect_uri = get_redirect_uri()
            
            # Note: This will raise an exception if we don't have a valid token
            # The frontend should handle this by redirecting to the login flow
            raise Exception("No valid credentials available. User needs to authenticate.")
    
    # Save the credentials for future use
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)
    
    return creds
