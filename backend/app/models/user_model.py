from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List
from bson import ObjectId

# OAuth schema object to enforce structure (Might not be necessary)
class OAuthSchema(BaseModel):
    token: str 
    refresh_token: Optional[str] = None
    token_uri: str
    client_id: str
    client_secret: str
    scopes: List[str]  # ✅ Allow `scopes` as a list

class UserSchema(BaseModel):
    google_id: str # Google User ID
    email: EmailStr
    name: str
    oauth: OAuthSchema  # Stores OAuth tokens (provider, access_token, refresh_token)

    preferences: Dict[str, bool] = {
        "summaries": True,
        "theme": "light",
        "fetch_frequency": "120"
    }