"""
Models module initialization.

This module provides access to all Pydantic models used throughout the application.
All model-related functionality should be imported from here.
"""

from typing import Type, Dict, Any

# Import all model schemas
from .email_models import EmailSchema, ReaderViewResponse
from .summary_models import SummarySchema
from .user_models import UserSchema, PreferencesSchema
from .auth_models import (
    TokenData,
    TokenResponse,
    AuthStatusResponse,
    ExchangeCodeRequest,
    RefreshTokenRequest,
    VerifyTokenRequest,
    AuthState
)

# Define base model type
ModelType = Type[Any]

# Export all models
__all__ = [
    # Base
    'ModelType',
    
    # Email Models
    'EmailSchema',
    'ReaderViewResponse',
    
    # Summary Models
    'SummarySchema',
    
    # User Models
    'UserSchema',
    'PreferencesSchema',
    
    # Auth Models
    'TokenData',
    'TokenResponse',
    'AuthStatusResponse',
    'ExchangeCodeRequest',
    'RefreshTokenRequest',
    'VerifyTokenRequest',
    'AuthState'
]