from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.models import UserSchema
from database import db


router = APIRouter()

