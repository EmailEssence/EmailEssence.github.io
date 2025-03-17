import logging
from typing import List, Optional, Annotated
from fastapi import APIRouter, HTTPException, Depends, Query
from contextlib import asynccontextmanager

from app.utils.config import Settings, get_settings, SummarizerProvider
from app.models import EmailSchema, SummarySchema
from app.services import email_service
from app.services.summarization.base import AdaptiveSummarizer
from app.services.summarization import (
  ProcessingStrategy, 
  OpenAIEmailSummarizer,
  GeminiEmailSummarizer
)
from app.services.summary_service import SummaryService

router = APIRouter()

# Create a global summary service instance
summary_service = SummaryService()

# Initialize the service before handling requests via dependency
async def initialize_summary_service():
    """Ensure summary service is initialized."""
    initialized = getattr(summary_service, "_initialized", False)
    if not initialized:
        await summary_service.initialize()
        setattr(summary_service, "_initialized", True)
    return summary_service

# Dependency to get initialized summary service
async def get_summary_service():
    return await initialize_summary_service()

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
        # TODO Add support for other providers : Deepseek, Local
        case _:
            raise HTTPException(
                status_code=500,
                detail=f"Unsupported summarizer provider: {settings.summarizer_provider}"
            )

@router.get("/", response_model=List[SummarySchema])
async def summarize_emails_endpoint(
    refresh: bool = Query(False, description="Force regeneration of summaries"),
    auto_generate: bool = Query(True, description="Auto-generate missing summaries"),
    summarizer: AdaptiveSummarizer[EmailSchema] = Depends(get_summarizer),
    summary_service: SummaryService = Depends(get_summary_service)
):
    """
    Fetch emails and generate summaries using the configured summarizer.
    
    Args:
        refresh: Whether to force regeneration of summaries
        
    Returns:
        List[SummarySchema]: List of generated email summaries
    """
    try:
        # Fetch emails
        emails_data = await email_service.fetch_emails()
        emails = [EmailSchema(**email_dict) for email_dict in emails_data]
        
        if not emails:
            return []
        
        # If not refreshing, try to get existing summaries first
        if not refresh:
            # Get list of email IDs
            email_ids = [email.email_id for email in emails]
            
            # Check which summaries already exist
            existing_summaries = []
            missing_emails = []
            
            for email in emails:
                summary = await summary_service.get_summary(email.email_id)
                if summary:
                    existing_summaries.append(summary)
                else:
                    missing_emails.append(email)
            
            # If all summaries exist, return them
            if not missing_emails:
                return existing_summaries
            
            # Otherwise, only summarize the missing ones if auto_generate is True
            if auto_generate:
                emails = missing_emails
            else:
                return existing_summaries
        
        # Generate new summaries for emails that need them
        new_summaries = await summarizer.summarize(
            emails,
            strategy=ProcessingStrategy.ADAPTIVE
        )
        
        # Store the new summaries
        await summary_service.save_summaries_batch(new_summaries)
        
        # Return all summaries (existing + new)
        if not refresh and 'existing_summaries' in locals():
            return existing_summaries + new_summaries
        
        return new_summaries
        
    except Exception as e:
        # Log the full error for debugging
        logging.error(f"Error generating summaries: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate email summaries"
        )

@router.post("/summarize", response_model=SummarySchema)
async def summarize_single_email(
    email: EmailSchema,
    refresh: bool = Query(False, description="Force regeneration of summary"),
    summarizer: AdaptiveSummarizer[EmailSchema] = Depends(get_summarizer),
    summary_service: SummaryService = Depends(get_summary_service)
):
    """
    Generate a summary for a single email.
    
    Args:
        email: Email to summarize
        refresh: Whether to force regeneration of the summary
        
    Returns:
        SummarySchema: Generated summary
    """
    try:
        # Check if summary already exists
        if not refresh:
            existing_summary = await summary_service.get_summary(email.email_id)
            if existing_summary:
                return existing_summary
        
        # Generate summary
        summaries = await summarizer.summarize(
            [email],
            strategy=ProcessingStrategy.SINGLE
        )
        
        summary = summaries[0]
        
        # Store the summary
        await summary_service.save_summary(summary)
        
        return summary
        
    except Exception as e:
        logging.error(f"Error summarizing email: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate email summary"
        )

@router.get("/all", response_model=List[SummarySchema])
async def get_all_summaries(
    skip: int = Query(0, ge=0, description="Number of summaries to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of summaries to return"),
    sort_by: str = Query("generated_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort direction (asc or desc)"),
    summary_service: SummaryService = Depends(get_summary_service)
):
    """
    Retrieve stored summaries with pagination and sorting.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        sort_by: Field to sort by
        sort_order: Sort direction ("asc" or "desc")
        
    Returns:
        List[SummarySchema]: List of summaries
    """
    try:
        return await summary_service.get_summaries(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except Exception as e:
        logging.error(f"Error retrieving summaries: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve email summaries"
        )

@router.get("/batch", response_model=List[SummarySchema])
async def get_summaries_by_ids(
    ids: List[str] = Query(..., description="List of email IDs to fetch summaries for"),
    summarizer: AdaptiveSummarizer[EmailSchema] = Depends(get_summarizer),
    summary_service: SummaryService = Depends(get_summary_service)
):
    """
    Retrieve multiple summaries by their email IDs, generating any that don't exist.
    
    Args:
        ids: List of email IDs to fetch summaries for
        
    Returns:
        List[SummarySchema]: List of found or newly generated summaries
    """
    try:
        # Get existing summaries first
        existing_summaries = await summary_service.get_summaries_by_ids(ids)
        
        # Check if we need to generate any missing summaries
        found_ids = {summary.email_id for summary in existing_summaries}
        missing_ids = [id for id in ids if id not in found_ids]
        
        # Generate any missing summaries
        new_summaries = []
        for email_id in missing_ids:
            try:
                summary = await summary_service.get_or_create_summary(email_id, summarizer)
                new_summaries.append(summary)
            except Exception as e:
                logging.warning(f"Could not auto-generate summary for email {email_id}: {e}")
                # Continue with other emails even if one fails
        
        # Combine existing and new summaries
        return existing_summaries + new_summaries
        
    except Exception as e:
        logging.error(f"Error retrieving/generating summaries by IDs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve email summaries"
        )

@router.get("/{email_id}", response_model=SummarySchema)
async def get_summary_by_id(
    email_id: str,
    summarizer: AdaptiveSummarizer[EmailSchema] = Depends(get_summarizer),
    summary_service: SummaryService = Depends(get_summary_service)
):
    """
    Retrieve a specific summary by email ID, generating it if not found.
    
    Args:
        email_id: ID of the email
        
    Returns:
        SummarySchema: Summary found or newly generated
    """
    try:
        return await summary_service.get_or_create_summary(email_id, summarizer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error retrieving/generating summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve summary for email {email_id}")

@router.delete("/{email_id}")
async def delete_summary(
    email_id: str,
    summary_service: SummaryService = Depends(get_summary_service)
):
    """
    Delete a specific summary.
    
    Args:
        email_id: ID of the email
        
    Returns:
        dict: Status message
        
    Raises:
        HTTPException: If summary not found
    """
    deleted = await summary_service.delete_summary(email_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Summary for email {email_id} not found"
        )
    return {"message": f"Summary for email {email_id} deleted"}

@router.get("/keyword/{keyword}", response_model=List[SummarySchema])
async def search_by_keyword(
    keyword: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    summary_service: SummaryService = Depends(get_summary_service)
):
    """
    Search for summaries containing a specific keyword.
    
    Args:
        keyword: Keyword to search for
        limit: Maximum number of results to return
        
    Returns:
        List[SummarySchema]: Matching summaries
    """
    try:
        results = await summary_service.search_by_keywords([keyword], limit=limit)
        return results
    except Exception as e:
        logging.error(f"Error searching summaries by keyword: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to search summaries"
        )

@router.get("/recent/{days}", response_model=List[SummarySchema])
async def get_recent_summaries(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    summary_service: SummaryService = Depends(get_summary_service)
):
    """
    Get summaries generated within recent days.
    
    Args:
        days: Number of days to look back
        limit: Maximum number of results to return
        
    Returns:
        List[SummarySchema]: Recent summaries
    """
    try:
        results = await summary_service.get_recent_summaries(days=days, limit=limit)
        return results
    except Exception as e:
        logging.error(f"Error retrieving recent summaries: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve recent summaries"
        )
