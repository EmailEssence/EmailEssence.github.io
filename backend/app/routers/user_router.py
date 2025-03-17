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
from app.services.user_service import get_or_create_user, create_user, get_user_by_id, update_user, delete_user
from database import db

router = APIRouter()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve user details or create user if they don't exist.
    """
    try:
        credentials = await run_in_threadpool(get_credentials)
        if not credentials.valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google OAuth token")
        
        service = await run_in_threadpool(lambda: build("oauth2", "v2", credentials=credentials))
        user_info = await run_in_threadpool(lambda: service.userinfo().get().execute())

        if not user_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to retrieve user info")
        
        user = await get_or_create_user(user_info)
        return user

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve user: {str(e)}")

@router.get("/{user_id}")
async def get_user(user_id: str):
    """
    Retrieve a user by ID.
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}")
async def update_user_info(user_id: str, user_data: dict):
    """
    Update user details.
    """
    updated_user = await update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or update failed")
    return updated_user

@router.delete("/{user_id}")
async def delete_user_info(user_id: str):
    """
    Delete a user by ID.
    """
    success = await delete_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or delete failed")
    return JSONResponse(content={"message": "User deleted successfully"}, status_code=status.HTTP_200_OK)

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

@router.get("/preferences")
async def get_user_preferences(token: str = Depends(oauth2_scheme)):
    """
    Retrieve user preferences without exposing the full user model.
    """
    try:
        credentials = await run_in_threadpool(get_credentials)
        if not credentials.valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google OAuth token")

        service = await run_in_threadpool(lambda: build("oauth2", "v2", credentials=credentials))
        user_info = await run_in_threadpool(lambda: service.userinfo().get().execute())

        if not user_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to retrieve user info")

        user = await db.users.find_one({"google_id": user_info["id"]}, {"preferences": 1, "_id": 0})

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return {"preferences": user.get("preferences", {})}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve user preferences: {str(e)}")

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
    