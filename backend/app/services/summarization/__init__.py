"""
Summarization module for Email Essence.

This module provides functionality for summarizing emails using various providers
and strategies.
"""

from typing import TypeVar, Generic
from fastapi import Depends, HTTPException

from app.utils.config import Settings, get_settings, SummarizerProvider
from app.models import EmailSchema
from .base import AdaptiveSummarizer
from .providers.openai.openai import OpenAIEmailSummarizer
from .providers.google.google import GeminiEmailSummarizer
from .types import ProcessingStrategy
from .summary_service import SummaryService

T = TypeVar('T')

__all__ = [
    'SummaryService',
    'ProcessingStrategy',
    'OpenAIEmailSummarizer',
    'GeminiEmailSummarizer',
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
        case _:
            raise HTTPException(
                status_code=500,
                detail=f"Unsupported summarizer provider: {settings.summarizer_provider}"
            )