import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from app.utils.config import Settings, get_settings, SummarizerProvider
from app.models import EmailSchema, SummarySchema
from app.services import email_service
from app.services.summarization.base import AdaptiveSummarizer
from app.services.summarization import (
  ProcessingStrategy, 
  OpenAIEmailSummarizer
)


router = APIRouter()

async def get_summarizer(
    settings: Settings = Depends(get_settings)
) -> AdaptiveSummarizer[EmailSchema]:
    """
    Factory function for creating the appropriate summarizer based on settings.
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
                model=settings.summarizer_model,
                batch_threshold=settings.summarizer_batch_threshold
            )
        # TODO Add support for other providers : Deepseek, Local
        case _:
            raise HTTPException(
                status_code=500,
                detail=f"Unsupported summarizer provider: {settings.summarizer_provider}"
            )

@router.get("/", response_model=List[SummarySchema])
async def summarize_emails_endpoint(
    summarizer: AdaptiveSummarizer[EmailSchema] = Depends(get_summarizer)
):
    """
    Fetch emails and generate summaries using the OpenAI-based summarizer.
    
    Returns:
        List[SummarySchema]: List of generated email summaries
    """
    try:
        # Fetch emails
        emails_data = await email_service.fetch_emails()
        emails = [EmailSchema(**email_dict) for email_dict in emails_data]
        
        if not emails:
            return []
        
        # Generate summaries
        summaries = await summarizer.summarize(
            emails,
            strategy=ProcessingStrategy.ADAPTIVE
        )
        
        return summaries
        
    except Exception as e:
        # Log the full error for debugging
        logging.error(f"Error generating summaries: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate email summaries"
        )

# TODO Add endpoint for single email summarization
@router.post("/summarize", response_model=SummarySchema)
async def summarize_single_email(
    email: EmailSchema,
    summarizer: OpenAIEmailSummarizer = Depends(get_summarizer)
):
    """
    Generate a summary for a single email.
    
    Args:
        email: Email to summarize
        
    Returns:
        SummarySchema: Generated summary
    """
    try:
        summaries = await summarizer.summarize(
            [email],
            strategy=ProcessingStrategy.SINGLE
        )
        return summaries[0]
        
    except Exception as e:
        logging.error(f"Error summarizing email: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate email summary"
        )
    
# Retrieve a specific summary
# @router.get("/{id}", response_model=Summary)

# Create a new summary
# @router.post("/", response_model=Summary)

# Delete a specific summary
# @router.delete("/{id}")