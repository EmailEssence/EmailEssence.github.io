"""
Factory functions for creating repository instances with caching.
"""

from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorCollection

from app.services.database.connection import get_database_connection
from app.services.database.email_repository import EmailRepository
from app.services.database.user_repository import UserRepository
from app.services.database.summary_repository import SummaryRepository
from app.services.database.token_repository import TokenRepository
from app.services.database.interfaces import IEmailRepository, IUserRepository, ISummaryRepository, ITokenRepository

@lru_cache()
def get_email_repository() -> IEmailRepository:
    """
    Factory function that returns an EmailRepository instance.
    Using lru_cache for efficiency so we don't create a new instance for every request.
    """
    db = get_database_connection()
    collection = db.get_collection("emails")
    return EmailRepository(collection)

@lru_cache()
def get_user_repository() -> IUserRepository:
    """
    Factory function that returns a UserRepository instance.
    Using lru_cache for efficiency so we don't create a new instance for every request.
    """
    db = get_database_connection()
    collection = db.get_collection("users")
    return UserRepository(collection)

@lru_cache()
def get_summary_repository() -> ISummaryRepository:
    """
    Factory function that returns a SummaryRepository instance.
    Using lru_cache for efficiency so we don't create a new instance for every request.
    """
    db = get_database_connection()
    collection = db.get_collection("summaries")
    return SummaryRepository(collection)

@lru_cache()
def get_token_repository() -> ITokenRepository:
    """
    Factory function that returns a TokenRepository instance.
    Using lru_cache for efficiency so we don't create a new instance for every request.
    """
    db = get_database_connection()
    collection = db.get_collection("tokens")
    return TokenRepository(collection) 