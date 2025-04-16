"""
Authentication router for Email Essence.

This module handles all authentication-related endpoints including OAuth2 flow with Google,
token management, and authentication status verification. It supports secure access to Gmail
via OAuth2 to retrieve and process email data.
"""

import json
import urllib.parse
import base64
import uuid
from typing import Dict, Optional, Any
from functools import lru_cache

from fastapi import APIRouter, HTTPException, status, Depends, Request, Query, Form
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, EmailStr
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from app.services.auth_service import AuthService, SCOPES
from app.services.user_service import UserService
from app.utils.config import get_settings
from app.services.database.factories import get_auth_service, get_user_service
from app.models import TokenData, TokenResponse, AuthStatusResponse, ExchangeCodeRequest, RefreshTokenRequest, VerifyTokenRequest

router = APIRouter()
settings = get_settings()

# -- Authentication Schemes --

# This is a simpler authentication scheme for Swagger UI
# It only shows a token field without client_id/client_secret
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", description="Enter the token you received from the login flow (without Bearer prefix)")

# -- Authentication Utility --

async def get_current_user_email(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Dependency to extract user email from valid token.
    Will raise 401 automatically if token is invalid.
    
    Args:
        token: JWT token from OAuth2 authentication
        auth_service: Auth service instance
        
    Returns:
        str: User's email address
        
    Raises:
        HTTPException: 401 error if token is invalid
    """
    try:
        # Get user info from token
        user_data = await auth_service.get_credentials_from_token(token)
        return user_data['email']
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# -- Endpoints --

# Debugging helper function
def debug(message: str):
    print(f"[DEBUG] {message}")

@router.get(
    "/login", 
    summary="Start Google OAuth login flow",
    description="Initiates the OAuth2 authentication process with Google. Redirects to Google's consent screen.",
    response_class=RedirectResponse
)
async def login(
    redirect_uri: str = Query(
        ..., 
        description="Frontend URI to redirect back to after authentication. Use http://localhost:8000/docs for Swagger testing."
    ),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Initiates the OAuth flow with Google, storing the frontend's redirect URI in the state parameter.
    For testing in Swagger UI, use 'http://localhost:8000/docs' as the redirect_uri.
    
    Args:
        redirect_uri: Frontend URI to redirect back to after successful authentication
        auth_service: Auth service instance
        
    Returns:
        RedirectResponse: Redirects to Google's authentication page
    """
    debug(f"Login initiated - Redirect URI: {redirect_uri}")

    try:
        # Create a state object that includes the frontend redirect URI
        custom_state = {
            "redirect_uri": redirect_uri,
            "nonce": str(uuid.uuid4())  # Add a nonce for security
        }

        # Encode the state as a base64 string
        encoded_custom_state = base64.urlsafe_b64encode(json.dumps(custom_state).encode()).decode()

        # Get the authorization URL from auth_service.py - PASS OUR STATE
        result = auth_service.create_authorization_url(encoded_custom_state)
        authorization_url = result["authorization_url"]

        debug(f"Generated Google OAuth URL: {authorization_url}")
        
        # Now redirect to the correct URL
        return RedirectResponse(authorization_url)

    except Exception as e:
        debug(f"[ERROR] Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create authorization URL: {str(e)}"
        )

@router.get("/callback")
async def callback(
    code: str, 
    state: str = Query(None),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Handles the OAuth callback from Google and exchanges the authorization code for access tokens.
    
    Args:
        code: Authorization code from Google
        state: State parameter containing encoded redirect URI
        auth_service: Auth service instance
        user_service: User service instance
        
    Returns:
        RedirectResponse: Redirects to frontend with authentication state
    """
    debug(f"Received callback with code: {code}")
    
    try:
        if not state:
            raise ValueError("Missing state parameter")
        
        # Decode state to retrieve frontend redirect URI
        decoded_state = json.loads(base64.urlsafe_b64decode(state).decode())
        frontend_url = decoded_state.get("redirect_uri")

        debug(f"Decoded state - Redirecting to frontend: {frontend_url}")

        if not frontend_url:
            raise ValueError("Missing redirect URI in state parameter")

        # Exchange code for tokens and get user info in one step
        debug("Exchanging code for tokens and getting user info...")
        token_data = await auth_service.get_tokens_from_code(code, None)  # First exchange
        
        # Get user info using the token
        credentials = Credentials(
            token=token_data.token,  # Access token as attribute
            token_uri=token_data.token_uri,
            client_id=token_data.client_id,
            client_secret=token_data.client_secret,
            scopes=token_data.scopes
        )
        
        service = await run_in_threadpool(lambda: 
            build('oauth2', 'v2', credentials=credentials)
        )
        
        user_info = await run_in_threadpool(lambda: 
            service.userinfo().get().execute()
        )
        
        user_email = user_info.get('email')
        debug(f"User email retrieved: {user_email}")
        
        if not user_email:
            raise ValueError("Could not retrieve user email from Google")
        
        # Check if user exists, create if not
        user = await user_service.get_user_by_email(user_email)
        if not user:
            debug(f"Creating new user: {user_email}")
            user = await user_service.create_user({
                "email": user_email,
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", ""),
                "google_id": user_info.get("id")
            })
        else:
            debug(f"Found existing user: {user_email}")
        
        # Special handling for Swagger UI testing
        if "localhost:8000/docs" in frontend_url or "/docs" in frontend_url:
            # Redirect to our token display page instead of back to Swagger directly
            return RedirectResponse(
                url=f"/auth/test-token-display?token={token_data.token}"
            )
            
        # Normal redirect for frontend apps
        auth_state = {
            "authenticated": True,
            "token": token_data.token
        }

        encoded_state = urllib.parse.quote(json.dumps(auth_state))
        return RedirectResponse(
            url=f"{frontend_url}/#auth={encoded_state}"
        )
    except Exception as e:
        error_msg = str(e)
        # If testing with Swagger, show the error on our token display page
        if frontend_url and ("localhost:8000/docs" in frontend_url or "/docs" in frontend_url):
            return RedirectResponse(f"/auth/test-token-display?error={urllib.parse.quote(error_msg)}")
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to get tokens: {error_msg}"
        )

@router.post("/exchange", response_model=TokenResponse)
async def exchange_code(
    request: ExchangeCodeRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Exchanges an authorization code for tokens and stores them in the database.
    Requires the user's email to associate the tokens.
    """
    
    debug(f"Exchanging OAuth code for user: {request.user_email}")
    try:
        if not request.code or not request.user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code and user email are required"
            )
        
        # Exchange auth code for tokens and store them in MongoDB
        tokens = await auth_service.get_tokens_from_code(request.code, request.user_email)
        
        debug(f"Token exchange successful for {request.user_email}")
        return TokenResponse(
            access_token=tokens.token,
            token_type="bearer",
            expires_in=3600,
            refresh_token=tokens.refresh_token
        )
        
    except Exception as e:
        debug(f"[ERROR] Code exchange failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to exchange code for tokens: {str(e)}"
        )

@router.get("/token", response_model=TokenResponse)
async def get_token(
    user_email: str = Query(...),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Retrieves the stored access token for the user.
    If expired, it will refresh the token automatically.
    """
    
    try:
        # Fetch stored token from MongoDB
        token = await auth_service.get_token_data(user_email)
        return TokenResponse(
            access_token=token.token,
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
    current_user_email: str = Depends(get_current_user_email),
    auth_service: AuthService = Depends(get_auth_service)
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
        token = await auth_service.get_token_data(request.user_email)
        return TokenResponse(
            access_token=token.token,
            token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.get("/status", response_model=AuthStatusResponse)
async def auth_status(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Returns the user's authentication status.
    Requires authentication.
    """
    
    try:
        # Extract user info from the token
        user_data = await auth_service.get_credentials_from_token(token)
        user_email = user_data['email']
        
        debug(f"User email extracted from token: {user_email}")
        
        # Get detailed credentials from the database using that email
        try:
            # Get the token record directly from the database instead of using get_credentials
            token_record = await auth_service.get_token_record(user_email)
            
            if not token_record:
                return AuthStatusResponse(
                    is_authenticated=True,
                    token_valid=True,
                    has_refresh_token=False,
                    error="No token record found in database"
                )
                
            return AuthStatusResponse(
                is_authenticated=True,
                token_valid=True,
                has_refresh_token=bool(token_record.get("refresh_token"))
            )
        except Exception as e:
            # The token is valid but we couldn't get stored credentials
            return AuthStatusResponse(
                is_authenticated=True,
                token_valid=True,
                has_refresh_token=False,
                error=f"No stored credentials: {str(e)}"
            )
            
    except Exception as e:
        # Token validation failed
        debug(f"[ERROR] Auth status check failed: {str(e)}")
        return AuthStatusResponse(
            is_authenticated=False,
            token_valid=False,
            error=str(e)
        )

@router.post("/verify")
async def verify_token(
    request: VerifyTokenRequest,
    token: str = Depends(oauth2_scheme),  # Requiring auth ensures only authenticated users can verify tokens
    auth_service: AuthService = Depends(get_auth_service)
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
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret
        )
        
        request_obj = GoogleRequest()
        credentials.refresh(request_obj)
        
        return {"verified": True}
        
    except Exception as e:
        return {"verified": False}

@router.get("/test-token-display", include_in_schema=False)
async def display_token_for_testing(token: str = Query(None), error: str = Query(None)):
    """
    Displays the token in a simple HTML page for copying into Swagger UI.
    Used for testing OAuth flow without a frontend.
    """
    if token:
        # Simple HTML page with the token
        html_content = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Auth Token for Testing</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .token-box {{ 
                        background-color: #f0f0f0; 
                        padding: 20px; 
                        border-radius: 5px;
                        word-break: break-all;
                    }}
                    .copy-btn {{
                        background-color: #4CAF50;
                        border: none;
                        color: white;
                        padding: 10px 15px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin: 10px 0;
                        cursor: pointer;
                        border-radius: 5px;
                    }}
                    .instructions {{
                        background-color: #e7f3fe;
                        border-left: 6px solid #2196F3;
                        padding: 15px;
                        margin: 20px 0;
                    }}
                    .note {{
                        background-color: #fffde7;
                        border-left: 6px solid #ffd600;
                        padding: 15px;
                        margin: 20px 0;
                    }}
                    img {{
                        max-width: 100%;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        padding: 5px;
                        margin: 10px 0;
                    }}
                </style>
            </head>
            <body>
                <h1>OAuth Token Successfully Generated</h1>
                
                <div class="instructions">
                    <h3>How to use this token in Swagger UI:</h3>
                    <ol>
                        <li>Copy the token below (use the copy button)</li>
                        <li>Go to <a href="/docs" target="_blank">Swagger UI</a></li>
                        <li>Click the green "Authorize" button at the top right of the page</li>
                        <li>In the authorization popup:</li>
                        <ul>
                            <li>Leave the username field as "oauth" (or enter anything)</li>
                            <li>Paste your token in the password field</li>
                        </ul>
                        <li>Click "Authorize" and close the dialog</li>
                        <li>Now you can test any protected endpoint!</li>
                    </ol>
                </div>
                
                <div class="note">
                    <h3>Important Notes:</h3>
                    <ul>
                        <li>This token is valid for a limited time only</li>
                        <li>If you get 401 Unauthorized errors, repeat the login process to get a new token</li>
                        <li>Your token contains sensitive information - do not share it</li>
                    </ul>
                </div>
                
                <p><strong>Your token:</strong></p>
                <div class="token-box" id="token">{token}</div>
                <button class="copy-btn" onclick="copyToken()">Copy Token</button>
                
                <script>
                function copyToken() {{
                    const tokenText = document.getElementById('token').innerText;
                    navigator.clipboard.writeText(tokenText)
                        .then(() => alert('Token copied to clipboard!'))
                        .catch(err => console.error('Error copying token: ', err));
                }}
                </script>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    elif error:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Authentication Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .error-box {{ 
                        background-color: #ffebee; 
                        padding: 20px; 
                        border-radius: 5px;
                        border-left: 6px solid #f44336;
                    }}
                    .troubleshooting {{
                        background-color: #f9f9f9;
                        padding: 15px;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <h1>Authentication Error</h1>
                <div class="error-box">
                    <p>{error}</p>
                </div>
                
                <div class="troubleshooting">
                    <h3>Troubleshooting Steps:</h3>
                    <ol>
                        <li>Try logging in again using <a href="/docs#/Auth/login_auth_login_get">this endpoint</a></li>
                        <li>Make sure your Google account has access to this application</li>
                        <li>Check if your environment variables for Google OAuth are correctly set</li>
                        <li>Verify that the redirect URI is properly configured in Google Developer Console</li>
                    </ol>
                </div>
                
                <p><a href="/docs">Return to Swagger UI</a></p>
            </body>
        </html>
        """)
    else:
        return HTMLResponse(content="<h1>No token provided</h1>")

@router.post("/token", summary="Store a Google token")
async def token_endpoint(
    username: str = Form("oauth", description="Just use 'oauth' here"),
    password: str = Form(..., description="Paste your Google token here"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Store a Google token in the database.
    
    Args:
        username: Not used, can be left as 'oauth'
        password: The Google token to store
    """
    try:
        token = password
        
        # Validate token and get user info
        validation_result = await auth_service.get_credentials_from_token(token)
        user_email = validation_result['email']
        google_id = validation_result['user_info']['google_id']
        
        # Store the token in our repository
        token_data = {
            "google_id": google_id,
            "token": token,
            "refresh_token": None,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "scopes": SCOPES
        }
        
        # Try to update by google_id first
        updated = await auth_service.token_repository.update_by_google_id(google_id, token_data)
        if not updated:
            # If update failed, try to insert new token
            await auth_service.token_repository.insert_one(TokenData(**token_data))
        
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to store token: {str(e)}"
        )