from .types import ProcessingStrategy
from .providers.openai import OpenAIEmailSummarizer
# Future provider imports as needed
# from .providers.deepseek import DeepSeekEmailSummarizer

__all__ = [
    'ProcessingStrategy',
    'OpenAIEmailSummarizer',
    # 'DeepSeekEmailSummarizer'
]