from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

from google.auth.transport.requests import Request
from starlette.concurrency import run_in_threadpool

from app.services import auth_service

router = APIRouter()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

@router.get("/authorize")
async def authorize():
    """
    Initiates the OAuth2 authorization flow with Google
    """
    try:
        credentials = await run_in_threadpool(auth_service.get_credentials)
        return {"token": credentials.token}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authorization failed: {str(e)}"
        )

@router.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    """
    Returns the current valid token or refreshes if expired
    """
    try:
        credentials = await run_in_threadpool(auth_service.get_credentials)
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                await run_in_threadpool(lambda: credentials.refresh(Request()))
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
    
@router.get("/internal/token", include_in_schema=False)
async def get_internal_token():
    """
    Internal endpoint for service-to-service communication.
    Not exposed in OpenAPI schema.
    """
    try:
        credentials = await run_in_threadpool(auth_service.get_credentials)
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                await run_in_threadpool(lambda: credentials.refresh(Request()))
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired and cannot be refreshed"
                )
        return {"access_token": credentials.token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Internal token retrieval failed: {str(e)}"
        )    

@router.post("/refresh")
async def refresh_token():
    """
    Forces a token refresh regardless of current token state
    """
    try:
        credentials = await run_in_threadpool(auth_service.get_credentials)
        if credentials.refresh_token:
            await run_in_threadpool(lambda: credentials.refresh(Request()))
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
        credentials = await run_in_threadpool(auth_service.get_credentials)
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