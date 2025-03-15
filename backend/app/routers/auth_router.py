import json
import urllib.parse
import base64
import uuid

from fastapi import APIRouter, HTTPException, status, Depends, Request, Body, Query
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from google.auth.transport.requests import Request as GoogleRequest
from starlette.concurrency import run_in_threadpool
from google.oauth2.credentials import Credentials
from typing import Dict

from app.services.auth_service import create_authorization_url, get_tokens_from_code, get_credentials

router = APIRouter()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

@router.get("/login")
async def login(redirect_uri: str = Query(..., description="Frontend URI to redirect back to after authentication")):
    """
    Initiates the OAuth flow with Google, storing the frontend's redirect URI in the state parameter
    """
    try:
        # Create a custom state that includes the redirect URI
        custom_state = {
            "redirect_uri": redirect_uri,
            "nonce": str(uuid.uuid4())  # Add a nonce for security
        }
        
        # Encode custom state to pass to Google
        encoded_custom_state = base64.urlsafe_b64encode(json.dumps(custom_state).encode()).decode()
        
        # Use the existing service to get the authorization URL
        authorization_url, _ = create_authorization_url()
        
        # Append our custom state to the authorization URL
        if '?' in authorization_url:
            authorization_url = authorization_url.split('&state=')[0]  # Remove any existing state
            authorization_url += f"&state={encoded_custom_state}"
        else:
            authorization_url += f"?state={encoded_custom_state}"
            
        return RedirectResponse(authorization_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create authorization URL: {str(e)}"
        )

@router.get("/callback")
async def callback(code: str, state: str = Query(None)):
    """
    Handles the OAuth callback from Google
    """
    try:
        # Decode the state parameter to get the frontend's redirect URI
        if not state:
            raise ValueError("Missing state parameter")
            
        decoded_state = json.loads(base64.urlsafe_b64decode(state).decode())
        frontend_url = decoded_state.get("redirect_uri")
        
        if not frontend_url:
            raise ValueError("Missing redirect URI in state parameter")
        
        tokens = await run_in_threadpool(lambda: get_tokens_from_code(code))
        
        # Add token to redirect URL as a hash parameter
        auth_state = {
            "authenticated": True,
            "token": tokens['token']
        }
        
        # URL encode the state
        encoded_state = urllib.parse.quote(json.dumps(auth_state))
        return RedirectResponse(
            url=f"{frontend_url}/#auth={encoded_state}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to get tokens: {str(e)}"
        )

@router.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    """
    Returns the current valid token or refreshes if expired
    """
    try:
        credentials = await run_in_threadpool(get_credentials)
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                await run_in_threadpool(lambda: credentials.refresh(GoogleRequest()))
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired and cannot be refreshed"
                )
        return {"access_token": credentials.token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token retrieval failed: {str(e)}"
        )

@router.post("/refresh")
async def refresh_token():
    """
    Forces a token refresh regardless of current token state
    """
    try:
        credentials = await run_in_threadpool(get_credentials)
        if credentials.refresh_token:
            await run_in_threadpool(lambda: credentials.refresh(GoogleRequest()))
            return {"access_token": credentials.token, "token_type": "bearer"}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No refresh token available"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.get("/status")
async def auth_status():
    """
    Returns the current authentication status and token validity
    """
    try:
        credentials = await run_in_threadpool(get_credentials)
        return {
            "is_authenticated": credentials is not None,
            "token_valid": credentials.valid if credentials else False,
            "token_expired": credentials.expired if credentials else True,
            "has_refresh_token": bool(credentials.refresh_token if credentials else False)
        }
    except Exception as e:
        return {
            "is_authenticated": False,
            "error": str(e)
        }

@router.post("/verify")
async def verify_token(data: Dict[str, str] = Body(...)):
    """
    Verifies token directly with Google
    Accepts token object in request body
    """
    try:
        token = data.get('token')
        if not token:
            return {"verified": False}

        # Create credentials object with just the token
        credentials = Credentials(
            token=token,
            token_uri="https://oauth2.googleapis.com/token"
        )
        
        # Try to refresh/verify the token
        request = Request()
        credentials.refresh(request)
        
        return {"verified": True}
        
    except Exception as e:
        # Any error means token is invalid
        return {"verified": False}

@router.post("/exchange")
async def exchange_code(data: Dict[str, str] = Body(...)):
    """
    Exchanges an authorization code for tokens
    Accepts the authorization code in the request body
    """
    try:
        code = data.get("code")
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code is required"
            )
        
        # Exchange the code for tokens
        tokens = await run_in_threadpool(lambda: get_tokens_from_code(code))
        
        # Return the tokens to the frontend
        return {
            "access_token": tokens["token"],
            "token_type": "bearer",
            "expires_in": 3600,  # Typical expiration time
            "refresh_token": tokens.get("refresh_token")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to exchange code for tokens: {str(e)}"
        )