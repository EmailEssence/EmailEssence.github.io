"""
Services module initialization.

This module provides access to all service implementations used throughout the application.
All service-related functionality should be imported from here.
"""

from typing import Type, Dict, Any

# Import all services
from .auth_service import AuthService
from .email_service import EmailService
from .user_service import UserService
from .summarization import (
    SummaryService,
    OpenAIEmailSummarizer,
    GeminiEmailSummarizer,
    ProcessingStrategy,
    get_summarizer
)

# Define base service type
ServiceType = Type[Any]

# Export all services and types
__all__ = [
    # Base
    'ServiceType',
    
    # Core Services
    'EmailService',
    'AuthService',
    'UserService',
    'SummaryService',
    
    # Summarization
    'OpenAIEmailSummarizer',
    'GeminiEmailSummarizer',
    'ProcessingStrategy',
    'get_summarizer'
]