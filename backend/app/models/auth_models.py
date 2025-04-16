"""
Authentication-related Pydantic models.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any

class TokenData(BaseModel):
    """
    Base model for OAuth token data.
    """
    google_id: str  # Shared index with UserSchema
    token: str
    refresh_token: Optional[str] = None
    token_uri: str
    client_id: str
    client_secret: str
    scopes: List[str]

class TokenResponse(BaseModel):
    """
    Response model for token-related endpoints.
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    refresh_token: Optional[str] = None

class AuthStatusResponse(BaseModel):
    """
    Response model for authentication status.
    """
    is_authenticated: bool
    token_valid: Optional[bool] = None
    has_refresh_token: Optional[bool] = None
    error: Optional[str] = None

class ExchangeCodeRequest(BaseModel):
    """
    Request model for exchanging an OAuth authorization code for tokens.
    """
    code: str
    user_email: EmailStr

class RefreshTokenRequest(BaseModel):
    """
    Request model for refreshing an access token.
    """
    user_email: EmailStr

class VerifyTokenRequest(BaseModel):
    """
    Request model for token verification.
    """
    token: str

class AuthState(BaseModel):
    """
    Model for authentication state passed to frontend.
    """
    authenticated: bool
    token: str