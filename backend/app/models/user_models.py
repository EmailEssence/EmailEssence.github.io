from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List
from bson import ObjectId
from app.models.auth_models import TokenData

class PreferencesSchema(BaseModel):
    """
    User preferences schema.
    """
    summaries: bool = True
    theme: str = "light"
    fetch_frequency: str = "120"

class UserSchema(BaseModel):
    """
    User schema for database operations.
    """
    google_id: str  # Google User ID
    email: EmailStr
    name: str
    preferences: PreferencesSchema = Field(default_factory=PreferencesSchema) 