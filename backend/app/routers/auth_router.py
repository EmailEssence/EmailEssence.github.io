import json
import urllib.parse

from fastapi import APIRouter, HTTPException, status, Depends, Request, Body
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from google.auth.transport.requests import Request as GoogleRequest
from starlette.concurrency import run_in_threadpool
from google.oauth2.credentials import Credentials

from app.services.auth_service import create_authorization_url, get_tokens_from_code, get_credentials

router = APIRouter()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

@router.get("/login")
async def login():
    """
    Initiates the OAuth2 authorization flow with Google
    """
    try:
        auth_url, state = await run_in_threadpool(create_authorization_url)
        return {"authorization_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create authorization URL: {str(e)}"
        )

@router.get("/callback")
async def callback(code: str):
    """
    Handles the OAuth callback from Google
    """
    try:
        tokens = await run_in_threadpool(lambda: get_tokens_from_code(code))
        
        # Get the appropriate frontend URL
        frontend_url = "https://emailessence.github.io"  # or use environment variable
        
        # Add token to redirect URL as a hash parameter
        # Using hash (#) instead of query (?) parameters for client-side only access
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
async def verify_token(token: str = Body(...)):
    """
    Verifies token directly with Google
    """
    try:
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