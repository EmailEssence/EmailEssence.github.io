"""
Database services module initialization.
"""

from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorCollection

from .connection import DatabaseConnection
from .base_repository import BaseRepository
from .email_repository import EmailRepository
from .user_repository import UserRepository
from .token_repository import TokenRepository
from .summary_repository import SummaryRepository
from .factories import (
    get_email_repository,
    get_user_repository,
    get_summary_repository,
    get_token_repository
)

__all__ = [
    'DatabaseConnection',
    'get_database_connection',
    'BaseRepository',
    'EmailRepository',
    'UserRepository',
    'TokenRepository',
    'SummaryRepository',
    'get_email_repository',
    'get_user_repository',
    'get_summary_repository',
    'get_token_repository'
] 