"""
Database services module initialization.

This module provides access to database repositories and connection management.
All database-related functionality should be imported from here.
"""

from functools import lru_cache
from typing import List, Type

from motor.motor_asyncio import AsyncIOMotorCollection

from .connection import DatabaseConnection
from .repositories.base_repository import BaseRepository
from .repositories.email_repository import EmailRepository
from .repositories.user_repository import UserRepository
from .repositories.token_repository import TokenRepository
from .repositories.summary_repository import SummaryRepository
from .factories import (
    get_email_repository,
    get_user_repository,
    get_summary_repository,
    get_token_repository
)

# Define available repository types
RepositoryType = Type[BaseRepository]
RepositoryTypes = List[RepositoryType]

# Export all repositories
__all__ = [
    # Connection
    'DatabaseConnection',
    'get_database_connection',
    
    # Base
    'BaseRepository',
    'RepositoryType',
    'RepositoryTypes',
    
    # Repositories
    'EmailRepository',
    'UserRepository',
    'TokenRepository',
    'SummaryRepository',
    
    # Factory functions
    'get_email_repository',
    'get_user_repository',
    'get_summary_repository',
    'get_token_repository'
] 