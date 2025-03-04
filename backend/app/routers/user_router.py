from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from models.user_model import UserSchema
from database import db


router = APIRouter()

