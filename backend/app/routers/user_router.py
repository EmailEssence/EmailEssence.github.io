from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.concurrency import run_in_threadpool

from app.models import UserSchema
from app.services.auth_service import get_tokens_from_code, get_credentials, get_credentials_from_token
from app.services.user_service import get_or_create_user, get_user_by_id, update_user, delete_user
from database import db

router = APIRouter()

# OAuth authentication scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", description="Enter the token you received from the login flow (without Bearer prefix)")

async def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """
    Validates token and returns user information.
    """
    try:
        user_data = await get_credentials_from_token(token)
        return user_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication: {str(e)}"
        )

@router.get("/me")
async def get_current_user(user_data: dict = Depends(get_current_user_info)):
    """
    Retrieve user details or create user if they don't exist.
    """
    try:
        user_info = user_data['user_info']
        credentials = user_data['credentials']
        
        user = await get_or_create_user(user_info, credentials)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )

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

@router.get("/preferences")
async def get_user_preferences(user_data: dict = Depends(get_current_user_info)):
    """
    Retrieve user preferences without exposing the full user model.
    """
    try:
        user_info = user_data['user_info']
        
        user = await db.users.find_one({"google_id": user_info["id"]}, {"preferences": 1, "_id": 0})

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return {"preferences": user.get("preferences", {})}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user preferences: {str(e)}"
        )

@router.put("/preferences")
async def update_preferences(
    preferences: dict, 
    user_data: dict = Depends(get_current_user_info)
):
    """
    Allows users to update their preferences.
    """
    try:
        user_info = user_data['user_info']
        
        await db.users.update_one(
            {"google_id": user_info["id"]},
            {"$set": {"preferences": preferences}}
        )
        return JSONResponse(content={"message": "Preferences updated successfully"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )
    