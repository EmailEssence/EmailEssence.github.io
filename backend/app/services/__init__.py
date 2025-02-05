from .auth_service import get_credentials
from .email_service import fetch_emails
from .summarization import OpenAIEmailSummarizer, ProcessingStrategy

# Export key types and implementations
__all__ = [
    'get_credentials', 
    'fetch_emails',
    'OpenAIEmailSummarizer',
    'ProcessingStrategy'
]