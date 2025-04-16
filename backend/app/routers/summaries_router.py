"""
Summaries router for Email Essence.

This module handles all operations related to email summaries, including generating summaries,
retrieving existing summaries, and managing summary data. It leverages various summarization
strategies to provide concise representations of emails.
"""

import logging
from typing import List, Optional, Annotated
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from contextlib import asynccontextmanager

from app.utils.config import Settings, get_settings, SummarizerProvider
from app.models import EmailSchema, SummarySchema, UserSchema
from app.services import EmailService, SummaryService
from app.services.summarization import get_summarizer
from app.services.summarization.base import AdaptiveSummarizer
from app.services.summarization import (
  ProcessingStrategy, 
  OpenAIEmailSummarizer,
  GeminiEmailSummarizer
)
from app.routers.user_router import get_current_user
from app.services.database.factories import (
    get_summary_service,
    get_email_service
)

# Configure logging with format and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Add specific configuration for pymongo's logger
logging.getLogger('pymongo').setLevel(logging.WARNING)

# Create module-specific logger
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{email_id}", response_model=SummarySchema)
async def get_summary_by_id(
    email_id: str,
    user: UserSchema = Depends(get_current_user),
    summary_service: SummaryService = Depends(get_summary_service),
    summarizer: AdaptiveSummarizer[EmailSchema] = Depends(get_summarizer)
):
    """
    Get a summary by email ID.
    
    Args:
        email_id: ID of the email to get summary for
        user: Current authenticated user
        summary_service: The summary service instance
        summarizer: The summarizer implementation to use
        
    Returns:
        SummarySchema: Summary for the specified email
    """
    try:
        # Get summary from repository
        summary = await summary_service.get_or_create_summary(email_id, summarizer, user.google_id)
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Summary not found for email {email_id}"
            )
            
        return SummarySchema(**summary)
        
    except Exception as e:
        logger.error(f"Error retrieving/generating summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/", 
    response_model=List[SummarySchema],
    summary="Get summaries for user's emails",
    description="Retrieves summaries for the current user's emails with option to regenerate"
)
async def summarize_emails_endpoint(
    refresh: bool = Query(False, description="Force regeneration of summaries"),
    auto_generate: bool = Query(True, description="Auto-generate missing summaries"),
    summarizer: AdaptiveSummarizer[EmailSchema] = Depends(get_summarizer),
    summary_service: SummaryService = Depends(get_summary_service),
    user: UserSchema = Depends(get_current_user)
):
    """
    Get summaries for all emails of the current user.
    
    Args:
        refresh: Whether to force regeneration of summaries
        auto_generate: Whether to automatically generate missing summaries
        summarizer: The summarizer implementation to use
        summary_service: The summary service for data operations
        user: Current authenticated user
        
    Returns:
        List[SummarySchema]: List of email summaries
        
    Raises:
        HTTPException: If summary retrieval or generation fails
    """
    try:
        # Fetch emails
        emails_data, _, _ = await email_service.fetch_emails(google_id=user.google_id)
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
                summary = await summary_service.get_summary(email.email_id, user.google_id)
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
        await summary_service.save_summaries_batch(new_summaries, user.google_id)
        
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

@router.post(
    "/summarize", 
    response_model=SummarySchema,
    summary="Summarize a single email",
    description="Generates or retrieves a summary for a single email"
)
async def summarize_single_email(
    email: EmailSchema,
    refresh: bool = Query(False, description="Force regeneration of summary"),
    summarizer: AdaptiveSummarizer[EmailSchema] = Depends(get_summarizer),
    summary_service: SummaryService = Depends(get_summary_service),
    user: UserSchema = Depends(get_current_user)
):
    """
    Generate a summary for a single email.
    
    Args:
        email: The email to summarize
        refresh: Whether to force regeneration of the summary
        summarizer: The summarizer implementation to use
        summary_service: The summary service for data operations
        user: Current authenticated user
        
    Returns:
        SummarySchema: Generated email summary
        
    Raises:
        HTTPException: If summary generation fails
    """
    try:
        # Check if summary already exists
        if not refresh:
            existing_summary = await summary_service.get_summary(email.email_id, user.google_id)
            if existing_summary:
                return existing_summary
        
        # Generate summary
        summaries = await summarizer.summarize(
            [email],
            strategy=ProcessingStrategy.SINGLE
        )
        
        summary = summaries[0]
        
        # Store the summary
        await summary_service.save_summary(summary, user.google_id)
        
        return summary
        
    except Exception as e:
        logging.error(f"Error summarizing email: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate email summary"
        )

@router.get(
    "/all", 
    response_model=List[SummarySchema],
    summary="Get all summaries",
    description="Retrieves all summaries with pagination, sorting, and filtering options"
)
async def get_all_summaries(
    skip: int = Query(0, ge=0, description="Number of summaries to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of summaries to return"),
    sort_by: str = Query("generated_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort direction (asc or desc)"),
    summary_service: SummaryService = Depends(get_summary_service),
    user: UserSchema = Depends(get_current_user)
):
    """
    Get all summaries with pagination and sorting.
    
    Args:
        skip: Number of summaries to skip (for pagination)
        limit: Maximum number of summaries to return
        sort_by: Field to sort by
        sort_order: Sort direction (asc or desc)
        summary_service: The summary service for data operations
        user: Current authenticated user
        
    Returns:
        List[SummarySchema]: Paginated list of summaries
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        return await summary_service.get_summaries(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            google_id=user.google_id
        )
    except Exception as e:
        logging.error(f"Error retrieving summaries: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve email summaries"
        )

@router.get(
    "/batch", 
    response_model=List[SummarySchema],
    summary="Get summaries by email IDs",
    description="Retrieves summaries for a batch of email IDs"
)
async def get_summaries_by_ids(
    ids: List[str] = Query(..., description="List of email IDs to fetch summaries for"),
    summarizer: AdaptiveSummarizer[EmailSchema] = Depends(get_summarizer),
    summary_service: SummaryService = Depends(get_summary_service),
    user: UserSchema = Depends(get_current_user)
):
    """
    Get summaries for a batch of email IDs.
    
    Args:
        ids: List of email IDs to fetch summaries for
        summarizer: The summarizer implementation to use
        summary_service: The summary service for data operations
        user: Current authenticated user
        
    Returns:
        List[SummarySchema]: List of summaries for the requested email IDs
        
    Raises:
        HTTPException: If batch retrieval fails
    """
    try:
        # Get existing summaries first
        existing_summaries = await summary_service.get_summaries_by_ids(ids, user.google_id)
        
        # Check if we need to generate any missing summaries
        found_ids = {summary.email_id for summary in existing_summaries}
        missing_ids = [id for id in ids if id not in found_ids]
        
        # Generate any missing summaries
        new_summaries = []
        for email_id in missing_ids:
            try:
                summary = await summary_service.get_or_create_summary(email_id, summarizer, user.google_id)
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

@router.delete(
    "/{email_id}",
    status_code=204,
    summary="Delete summary",
    description="Deletes a summary for a specific email"
)
async def delete_summary(
    email_id: str,
    summary_service: SummaryService = Depends(get_summary_service),
    user: UserSchema = Depends(get_current_user)
):
    """
    Delete a summary for a specific email ID.
    
    Args:
        email_id: ID of the email whose summary should be deleted
        summary_service: The summary service for data operations
        user: Current authenticated user
        
    Returns:
        None
        
    Raises:
        HTTPException: If the summary cannot be deleted
    """
    deleted = await summary_service.delete_summary(email_id, user.google_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Summary for email {email_id} not found"
        )
    return {"message": f"Summary for email {email_id} deleted"}

@router.get(
    "/keyword/{keyword}", 
    response_model=List[SummarySchema],
    summary="Search summaries by keyword",
    description="Retrieves summaries that contain the specified keyword"
)
async def search_by_keyword(
    keyword: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    summary_service: SummaryService = Depends(get_summary_service),
    user: UserSchema = Depends(get_current_user)
):
    """
    Search summaries by keyword.
    
    Args:
        keyword: The search term to look for in summaries
        limit: Maximum number of results to return
        summary_service: The summary service for data operations
        user: Current authenticated user
        
    Returns:
        List[SummarySchema]: List of summaries containing the keyword
        
    Raises:
        HTTPException: If the search fails
    """
    try:
        results = await summary_service.search_by_keywords([keyword], limit=limit, google_id=user.google_id)
        return results
    except Exception as e:
        logging.error(f"Error searching summaries by keyword: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to search summaries"
        )

@router.get("/recent/{days}", response_model=List[SummarySchema])
async def get_recent_summaries(
    days: int = Path(..., description="Number of days to look back"),
    limit: int = Query(20, description="Maximum number of summaries to return"),
    summary_service: SummaryService = Depends(get_summary_service),
    user: UserSchema = Depends(get_current_user)
) -> List[SummarySchema]:
    """
    Get summaries generated within recent days.
    
    Args:
        days: Number of days to look back
        limit: Maximum number of summaries to return
        user: Currently authenticated user
        
    Returns:
        List[SummarySchema]: Recent summaries
    """
    try:
        # Log request parameters
        logger.debug(f"Getting recent summaries for user {user.email} - days: {days}, limit: {limit}")
        
        # Get summaries from service
        summaries = await summary_service.get_recent_summaries(
            days=days,
            limit=limit,
            google_id=user.google_id
        )
        
        logger.debug(f"Retrieved {len(summaries)} summaries for user {user.email}")
        return summaries
    except Exception as e:
        logger.error(
            f"Error retrieving recent summaries for user {user.email}: {str(e)}",
            exc_info=True,
            extra={
                "user_email": user.email,
                "days": days,
                "limit": limit
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent summaries"
        )
