import os
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
from fastapi import HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict
from app.models import UserSchema
from database import db

load_dotenv()

SCOPES = [
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid',
    'https://www.googleapis.com/auth/userinfo.profile'
]

class TokenData(BaseModel):
    token: str
    refresh_token: Optional[str] = None
    token_uri: str
    client_id: str
    client_secret: str
    scopes: list

def create_authorization_url() -> Dict[str, str]:
    """ Generates Google OAuth2 authorization URL """
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

async def get_tokens_from_code(code: str, user_email: str) -> Dict[str, str]:
    """ Exchanges authorization code for access & refresh tokens, then stores them in the database """
    try:
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

        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        # Store in MongoDB
        await db.tokens.update_one(
            {"user_email": user_email},
            {"$set": token_data},
            upsert=True
        )

        return token_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Auth code exchange failed: {str(e)}")

async def get_credentials(user_email: str) -> Optional[TokenData]:
    """ Retrieves credentials from the database, refreshing the token if needed """
    token_record = await db.tokens.find_one({"user_email": user_email})
    
    if not token_record:
        raise HTTPException(status_code=401, detail="No credentials found. User needs to authenticate.")

    credentials = TokenData(**token_record)

    if not credentials.token:
        raise HTTPException(status_code=401, detail="Invalid token stored. Please re-authenticate.")

    # Refresh if expired
    if credentials.refresh_token:
        try:
            flow = Flow.from_client_config({
                "web": {
                    "client_id": credentials.client_id,
                    "client_secret": credentials.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [get_redirect_uri()]
                }
            }, SCOPES)
            flow.credentials.refresh(Request())

            # Update the database with the new token
            await db.tokens.update_one(
                {"user_email": user_email},
                {"$set": {"token": flow.credentials.token}}
            )

            return flow.credentials.token

        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")

    return credentials.token

def get_redirect_uri():
    """ Returns the backend callback URL for OAuth """
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
