from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from bson import ObjectId

class UserSchema(BaseModel):
    email: EmailStr
    name: str
    oauth: Dict[str, str]  # Stores OAuth tokens (provider, access_token, refresh_token)
    preferences: Optional[Dict[str, str]] = {
        "summary_length": "short",
        "theme": "light",
        "fetch_frequency": "30m"
    }