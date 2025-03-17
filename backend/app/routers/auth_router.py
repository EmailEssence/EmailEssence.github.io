import json
import urllib.parse
import base64
import uuid
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, EmailStr

from app.services.auth_service import create_authorization_url, get_tokens_from_code, get_credentials, get_credentials_from_token

router = APIRouter()

# -- Authentication Schemes --

# For protected endpoints that require authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# OAuth flow for Google authentication
google_oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

# -- Pydantic Models --

class ExchangeCodeRequest(BaseModel):
    code: str
    user_email: EmailStr

class RefreshTokenRequest(BaseModel):
    user_email: EmailStr

class VerifyTokenRequest(BaseModel):
    token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int = 3600
    refresh_token: Optional[str] = None

class AuthStatusResponse(BaseModel):
    is_authenticated: bool
    token_valid: Optional[bool] = None
    has_refresh_token: Optional[bool] = None
    error: Optional[str] = None

# -- Authentication Utility --

async def get_current_user_email(token: str = Depends(oauth2_scheme)):
    """
    Dependency to extract user email from valid token.
    Will raise 401 automatically if token is invalid.
    """
    try:
        # Get user info from token
        user_data = await run_in_threadpool(lambda: get_credentials_from_token(token))
        return user_data['email']
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# -- Endpoints --

@router.get("/login")
async def login(redirect_uri: str = Query(..., description="Frontend URI to redirect back to after authentication")):
    """
    Initiates the OAuth flow with Google, storing the frontend's redirect URI in the state parameter.
    """
    try:
        # Create a state object that includes the frontend redirect URI
        custom_state = {
            "redirect_uri": redirect_uri,
            "nonce": str(uuid.uuid4())  # Add a nonce for security
        }
        
        # Encode the state as a base64 string
        encoded_custom_state = base64.urlsafe_b64encode(json.dumps(custom_state).encode()).decode()
        
        # Get the authorization URL from auth_service.py
        authorization_url, _ = create_authorization_url()
        
        # Append the state parameter to the authorization URL
        authorization_url += f"&state={encoded_custom_state}"
        
        return RedirectResponse(authorization_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create authorization URL: {str(e)}"
        )

@router.get("/callback")
async def callback(code: str, state: str = Query(None)):
    """
    Handles the OAuth callback from Google and exchanges the authorization code for access tokens.
    """
    try:
        if not state:
            raise ValueError("Missing state parameter")
        
        # Decode state to retrieve frontend redirect URI
        decoded_state = json.loads(base64.urlsafe_b64decode(state).decode())
        frontend_url = decoded_state.get("redirect_uri")

        if not frontend_url:
            raise ValueError("Missing redirect URI in state parameter")

        # Exchange authorization code for access tokens
        tokens = await run_in_threadpool(lambda: get_tokens_from_code(code, None))  # No user email in callback

        # Redirect user to frontend with token
        auth_state = {
            "authenticated": True,
            "token": tokens['token']
        }

        encoded_state = urllib.parse.quote(json.dumps(auth_state))
        return RedirectResponse(
            url=f"{frontend_url}/#auth={encoded_state}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to get tokens: {str(e)}"
        )

@router.post("/exchange", response_model=TokenResponse)
async def exchange_code(request: ExchangeCodeRequest):
    """
    Exchanges an authorization code for tokens and stores them in the database.
    Requires the user's email to associate the tokens.
    """
    try:
        if not request.code or not request.user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code and user email are required"
            )
        
        # Exchange auth code for tokens and store them in MongoDB
        tokens = await run_in_threadpool(lambda: get_tokens_from_code(request.code, request.user_email))
        
        return TokenResponse(
            access_token=tokens["token"],
            token_type="bearer",
            expires_in=3600,
            refresh_token=tokens.get("refresh_token")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to exchange code for tokens: {str(e)}"
        )

@router.get("/token", response_model=TokenResponse)
async def get_token(user_email: str = Query(...)):
    """
    Retrieves the stored access token for the user.
    If expired, it will refresh the token automatically.
    """
    try:
        # Fetch stored token from MongoDB
        token = await run_in_threadpool(lambda: get_credentials(user_email))
        return TokenResponse(
            access_token=token,
            token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token retrieval failed: {str(e)}"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Forces a refresh of the user's token, if a refresh token is available.
    Requires authentication.
    """
    try:
        # Security check: only allow refreshing your own token
        if current_user_email != request.user_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only refresh your own token"
            )

        # Refresh token using stored credentials in MongoDB
        token = await run_in_threadpool(lambda: get_credentials(request.user_email))
        return TokenResponse(
            access_token=token,
            token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.get("/status", response_model=AuthStatusResponse)
async def auth_status(
    user_email: str = Query(...),
    token: str = Depends(oauth2_scheme)
):
    """
    Returns the user's authentication status.
    Requires authentication.
    """
    try:
        credentials = await run_in_threadpool(lambda: get_credentials(user_email))
        return AuthStatusResponse(
            is_authenticated=credentials is not None,
            token_valid=credentials is not None,
            has_refresh_token=bool(credentials.refresh_token if credentials else False)
        )
    except Exception as e:
        return AuthStatusResponse(
            is_authenticated=False,
            error=str(e)
        )

@router.post("/verify")
async def verify_token(
    request: VerifyTokenRequest,
    token: str = Depends(oauth2_scheme)  # Requiring auth ensures only authenticated users can verify tokens
):
    """
    Verifies a given access token by refreshing it.
    Requires authentication.
    """
    try:
        if not request.token:
            return {"verified": False}

        # Validate token with Google OAuth
        credentials = Credentials(
            token=request.token,
            token_uri="https://oauth2.googleapis.com/token"
        )
        
        request_obj = GoogleRequest()
        credentials.refresh(request_obj)
        
        return {"verified": True}
        
    except Exception as e:
        return {"verified": False}