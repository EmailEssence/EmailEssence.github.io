from typing import Callable
from app.repositories.email_repository import EmailRepository
from app.repositories.user_repository import UserRepository
from app.repositories.summary_repository import SummaryRepository
from app.repositories.interfaces import IEmailRepository, IUserRepository, ISummaryRepository

def get_email_repository() -> Callable[[], IEmailRepository]:
    """Factory function for email repository"""
    def _get_repo() -> IEmailRepository:
        return EmailRepository()
    return _get_repo

def get_user_repository() -> Callable[[], IUserRepository]:
    """Factory function for user repository"""
    def _get_repo() -> IUserRepository:
        return UserRepository()
    return _get_repo

def get_summary_repository() -> Callable[[], ISummaryRepository]:
    """Factory function for summary repository"""
    def _get_repo() -> ISummaryRepository:
        return SummaryRepository()
    return _get_repo 