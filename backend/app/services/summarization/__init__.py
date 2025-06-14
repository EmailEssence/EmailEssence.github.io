"""
Summarization module for Email Essence.

This module provides functionality for summarizing emails using various providers
and strategies.
"""

# Standard library imports
from typing import TypeVar, Generic

# Third-party imports
from fastapi import Depends, HTTPException

# Internal imports
from app.models import EmailSchema
from app.utils.config import Settings, get_settings, SummarizerProvider
from .base import AdaptiveSummarizer
from .providers.openai.openai import OpenAIEmailSummarizer
from .providers.google.google import GeminiEmailSummarizer
from .providers.openrouter.openrouter import OpenRouterEmailSummarizer
from .types import ProcessingStrategy
from .summary_service import SummaryService

T = TypeVar('T')

__all__ = [
    'SummaryService',
    'ProcessingStrategy',
    'OpenAIEmailSummarizer',
    'GeminiEmailSummarizer',
    'OpenRouterEmailSummarizer',
    'get_summarizer'
]

async def get_summarizer(
    settings: Settings = Depends(get_settings)
) -> AdaptiveSummarizer[EmailSchema]:
    """
    Factory function for creating the appropriate summarizer based on settings.
    
    Args:
        settings: Application settings containing summarizer configuration
        
    Returns:
        AdaptiveSummarizer: Configured email summarizer implementation
        
    Raises:
        HTTPException: If the configured summarizer provider is not supported
    """
    match settings.summarizer_provider:
        case SummarizerProvider.OPENAI:
            if not settings.openai_api_key:
                raise HTTPException(
                    status_code=500,
                    detail="OpenAI API key not configured"
                )
            return OpenAIEmailSummarizer(
                api_key=settings.openai_api_key,
                prompt_version=settings.summarizer_prompt_version,
                model=settings.summarizer_model,
                batch_threshold=settings.summarizer_batch_threshold
            )
        case SummarizerProvider.GOOGLE:
            if not settings.google_api_key:
                raise HTTPException(
                    status_code=500,
                    detail="Google API key not configured"
                )
            return GeminiEmailSummarizer(
                api_key=settings.google_api_key,
                prompt_version=settings.summarizer_prompt_version,
                model=settings.summarizer_model,
                batch_threshold=settings.summarizer_batch_threshold
            )
        case SummarizerProvider.OPENROUTER:
            if not settings.openrouter_api_key:
                raise HTTPException(
                    status_code=500,
                    detail="OpenRouter API key not configured"
                )
            return OpenRouterEmailSummarizer(
                api_key=settings.openrouter_api_key,
                prompt_version=settings.summarizer_prompt_version,
                batch_threshold=settings.summarizer_batch_threshold
            )
        case _:
            raise HTTPException(
                status_code=500,
                detail=f"Unsupported summarizer provider: {settings.summarizer_provider}"
            )