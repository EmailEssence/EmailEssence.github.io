"""
Factory functions for creating repository and service instances.
"""

from functools import lru_cache
from typing import Optional
import logging

from app.services.database.connection import instance
from app.services.database.email_repository import EmailRepository
from app.services.database.user_repository import UserRepository
from app.services.database.token_repository import TokenRepository
from app.services.database.summary_repository import SummaryRepository

@lru_cache()
def get_email_repository() -> EmailRepository:
    """
    Get a cached instance of EmailRepository.
    
    Returns:
        EmailRepository: Cached repository instance
    """
    repo = EmailRepository(instance.db.emails)
    return repo

@lru_cache()
def get_user_repository() -> UserRepository:
    """
    Get a cached instance of UserRepository.
    
    Returns:
        UserRepository: Cached repository instance
    """
    repo = UserRepository(instance.db.users)
    return repo

@lru_cache()
def get_token_repository() -> TokenRepository:
    """
    Get a cached instance of TokenRepository.
    
    Returns:
        TokenRepository: Cached repository instance
    """
    repo = TokenRepository(instance.db.tokens)
    return repo

@lru_cache()
def get_summary_repository() -> SummaryRepository:
    """
    Get a cached instance of SummaryRepository.
    
    Returns:
        SummaryRepository: Cached repository instance
    """
    repo = SummaryRepository(instance.db.summaries)
    return repo

@lru_cache()
def get_auth_service() -> 'AuthService': # type: ignore
    """
    Get a cached instance of AuthService.
    
    Returns:
        AuthService: Cached service instance
    """
    from app.services.auth_service import AuthService
    return AuthService(
        token_repository=get_token_repository(),
        user_repository=get_user_repository()
    )

@lru_cache()
def get_user_service() -> 'UserService': # type: ignore
    """
    Get a cached instance of UserService.
    
    Returns:
        UserService: Cached service instance
    """
    from app.services.user_service import UserService
    return UserService(user_repository=get_user_repository())

@lru_cache()
def get_email_service() -> 'EmailService': # type: ignore
    """
    Get a cached instance of EmailService.
    
    Returns:
        EmailService: Cached service instance
    """
    from app.services.email_service import EmailService
    return EmailService(email_repository=get_email_repository())

@lru_cache()
def get_summary_service() -> 'SummaryService': # type: ignore
    """
    Get a cached instance of SummaryService.
    
    Returns:
        SummaryService: Cached service instance
    """
    from app.services.summarization.summary_service import SummaryService
    return SummaryService(summary_repository=get_summary_repository())

async def setup_all_repositories():
    """
    Set up all repositories by creating their indexes.
    This should be called during application startup.
    """
    try:
        # Get all repositories
        email_repo = get_email_repository()
        user_repo = get_user_repository()
        token_repo = get_token_repository()
        summary_repo = get_summary_repository()
        
        # Setup indexes for all repositories
        await email_repo.setup_indexes()
        await user_repo.setup_indexes()
        await token_repo.setup_indexes()
        await summary_repo.setup_indexes()
        
        return True
    except Exception as e:
        logging.error(f"Failed to set up repositories: {str(e)}")
        return False

# Add to __all__ exports 