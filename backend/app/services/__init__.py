from .auth_service import AuthService
from .email_service import EmailService
from .user_service import UserService
from .summarization import SummaryService, OpenAIEmailSummarizer, ProcessingStrategy

# Export key types and implementations
__all__ = [
    'EmailService',
    'SummaryService',
    'AuthService',
    'UserService',
    'OpenAIEmailSummarizer',
    'ProcessingStrategy'
]