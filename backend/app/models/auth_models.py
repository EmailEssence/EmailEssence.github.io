from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class TokenSchema(BaseModel):
    token: str
    refresh_token: Optional[str] = None
    token_uri: str
    client_id: str
    client_secret: str
    scopes: list

# OAuth schema object to enforce structure (Might not be necessary)
class OAuthSchema(BaseModel):
    token: str 
    refresh_token: Optional[str] = None
    token_uri: str
    client_id: str
    client_secret: str
    scopes: List[str]  # ✅ Allow `scopes` as a list