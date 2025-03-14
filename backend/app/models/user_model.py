from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from bson import ObjectId

class UserSchema(BaseModel):
    google_id: str = Field(..., alias="sub")  # Google User ID
    email: EmailStr
    name: str
    oauth: Dict[str, str]  # Stores OAuth tokens (provider, access_token, refresh_token)

    preferences: Dict[str, bool] = {
        "summaries": True,
        "theme": "light",
        "fetch_frequency": "120"
    }

    class Config:
        allow_population_by_field_name = True