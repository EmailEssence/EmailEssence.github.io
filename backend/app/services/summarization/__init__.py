from .types import ProcessingStrategy
from app.services.summarization.providers.openai.openai import OpenAIEmailSummarizer
from app.services.summarization.providers.google.google import GeminiEmailSummarizer
from app.services.summarization.summary_service import SummaryService
# Future provider imports as needed
# from .providers.deepseek import DeepSeekEmailSummarizer

__all__ = [
    'SummaryService',
    'ProcessingStrategy',
    'OpenAIEmailSummarizer',
    'GeminiEmailSummarizer'
    
    # 'DeepSeekEmailSummarizer'
]