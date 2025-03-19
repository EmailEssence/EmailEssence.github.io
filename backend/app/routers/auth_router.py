import json
import urllib.parse
import base64
import uuid
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status, Depends, Request, Query, Form
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, EmailStr
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from database import db

from app.services.auth_service import create_authorization_url, get_tokens_from_code, get_credentials, get_credentials_from_token, SCOPES, get_redirect_uri
from app.services.user_service import get_or_create_user
from app.utils.config import get_settings

router = APIRouter()
settings = get_settings()

# -- Authentication Schemes --

# This is a simpler authentication scheme for Swagger UI
# It only shows a token field without client_id/client_secret
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", description="Enter the token you received from the login flow (without Bearer prefix)")

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
        user_data = await get_credentials_from_token(token)
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

@router.get("/login", description="Start the OAuth process to get access to protected endpoints. Set redirect_uri to 'http://localhost:8000/docs' for testing in Swagger.")
async def login(redirect_uri: str = Query(..., description="Frontend URI to redirect back to after authentication. Use http://localhost:8000/docs for Swagger testing.")):
    """
    Initiates the OAuth flow with Google, storing the frontend's redirect URI in the state parameter.
    For testing in Swagger UI, use 'http://localhost:8000/docs' as the redirect_uri.
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
        result = create_authorization_url(encoded_custom_state)
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
async def callback(code: str, state: str = Query(None)):
    """
    Handles the OAuth callback from Google and exchanges the authorization code for access tokens.
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

        # Exchange code for tokens - But we need to get the user email to store properly
        # First exchange without storing
        client_id = settings.google_client_id
        client_secret = settings.google_client_secret

        client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [get_redirect_uri()]
            }
        }

        # Create a flow to exchange code for credentials
        flow = Flow.from_client_config(
            client_config=client_config,
            scopes=SCOPES
        )
        flow.redirect_uri = get_redirect_uri()
        
        # Get tokens from the authorization code
        debug("Fetching OAuth token from Google...")
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        debug("OAuth token successfully retrieved")

        # Now use the credentials to get user info and extract email
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
        
        # Now properly store the tokens with the user email
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Store in MongoDB
        debug(f"Storing tokens in database for {user_email}...")
        await db.tokens.update_one(
            {"user_email": user_email},
            {"$set": token_data},
            upsert=True
        )
        debug("Tokens successfully stored in database")
        
        # Store user in database if not found
        user = await get_or_create_user(user_info, credentials)  # Create user if not found
        debug(f"User ensured in database: {user.get('email', 'Unknown')}")

        # Prepare auth response for frontend
        auth_state = {
            "authenticated": True,
            "token": credentials.token
        }
        
        
        # Special handling for Swagger UI testing
        if "localhost:8000/docs" in frontend_url or "/docs" in frontend_url:
            # Redirect to our token display page instead of back to Swagger directly
            return RedirectResponse(
                url=f"/auth/test-token-display?token={token_data['token']}"
            )
            
        # Normal redirect for frontend apps
        auth_state = {
            "authenticated": True,
            "token": token_data['token']
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
async def exchange_code(request: ExchangeCodeRequest):
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
        tokens = await run_in_threadpool(lambda: get_tokens_from_code(request.code, request.user_email))
        
        debug(f"Token exchange successful for {request.user_email}")
        return TokenResponse(
            access_token=tokens["token"],
            token_type="bearer",
            expires_in=3600,
            refresh_token=tokens.get("refresh_token")
        )
        
    except Exception as e:
        debug(f"[ERROR] Code exchange failed: {str(e)}")
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
async def auth_status(token: str = Depends(oauth2_scheme)):
    """
    Returns the user's authentication status.
    Requires authentication.
    """
    
    try:
        # Extract user info from the token
        user_data = await get_credentials_from_token(token)
        user_email = user_data['email']
        
        debug(f"User email extracted from token: {user_email}")
        
        # Get detailed credentials from the database using that email
        try:
            # Get the token record directly from the database instead of using get_credentials
            token_record = await db.tokens.find_one({"user_email": user_email})
            
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

@router.post("/token", summary="For Swagger UI auth only - paste your Google token here")
async def token_endpoint(
    username: str = Form("oauth", description="Just use 'oauth' here"),
    password: str = Form(..., description="Paste your Google token here")
):
    """
    This endpoint is for Swagger UI authentication only.
    
    Just paste your Google token in the password field.
    The username field is not used - you can leave it as 'oauth'.
    """
    try:
        # We'll use the password field as the token
        token = password
        
        # Validate the token to ensure it works
        await get_credentials_from_token(token)
        
        # Return a standard OAuth2 token response
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )