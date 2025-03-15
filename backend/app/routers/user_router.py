from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import JSONResponse

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.concurrency import run_in_threadpool

from app.models import UserSchema
from app.services.auth_service import get_tokens_from_code, get_credentials
from app.services.user_service import get_or_create_user
from database import db

router = APIRouter()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieves user details or creates the user if they don't exist.
    """
    try:
        credentials = await run_in_threadpool(get_credentials)
        if not credentials.valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google OAuth token")

        service = await run_in_threadpool(lambda: build("oauth2", "v2", credentials=credentials))
        user_info = await run_in_threadpool(lambda: service.userinfo().get().execute())

        if not user_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to retrieve user info")

        # Use `get_or_create_user` instead of manually checking the database
        user = await get_or_create_user(user_info, credentials)
        return user

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve user: {str(e)}")


@router.put("/preferences")
async def update_preferences(preferences: dict, token: str = Depends(oauth2_scheme)):
    """
    Allows users to update their preferences.
    """
    try:
        credentials = await run_in_threadpool(get_credentials)
        if not credentials.valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google OAuth token")
        
        service = await run_in_threadpool(lambda: build("oauth2", "v2", credentials=credentials))
        user_info = await run_in_threadpool(lambda: service.userinfo().get().execute())

        if not user_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to retrieve user info")
        
        await db.users.update_one(
            {"google_id": user_info["id"]},
            {"$set": {"preferences": preferences}}
        )
        return JSONResponse(content={"message": "Preferences updated successfully"}, status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update preferences: {str(e)}")
