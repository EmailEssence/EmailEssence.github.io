"""
Summaries router for Email Essence.

This module handles all operations related to email summaries, including generating summaries,
retrieving existing summaries, and managing summary data. It leverages various summarization
strategies to provide concise representations of emails.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status

from app.models import EmailSchema, SummarySchema, UserSchema
from app.services import SummaryService
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

# Add specific configuration for pymongo's logger
logging.getLogger('pymongo').setLevel(logging.WARNING)

# Create module-specific logger
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/batch", 
    response_model=List[SummarySchema],
    summary="Get summaries by email IDs",
    description="Retrieves summaries for a batch of email IDs"
)
async def get_summaries_by_ids(
    ids: List[str] = Query(..., description="List of email IDs to fetch summaries for"),
    batch_size: int = Query(50, ge=1, le=100, description="Maximum number of emails to process in a single batch"),
    summarizer: AdaptiveSummarizer[EmailSchema] = Depends(get_summarizer),
    summary_service: SummaryService = Depends(get_summary_service),
    user: UserSchema = Depends(get_current_user)
):
    """
    Get summaries for a batch of email IDs.
    
    Args:
        ids: List of email IDs to fetch summaries for
        batch_size: Maximum number of emails to process in a single batch
        summarizer: The summarizer implementation to use
        summary_service: The summary service for data operations
        user: Current authenticated user
        
    Returns:
        List[SummarySchema]: List of summaries for the requested email IDs
        
    Raises:
        HTTPException: If batch retrieval fails
    """
    try:
        if not ids:
            return []
            
        # Process batch of summaries
        result = await summary_service.get_or_create_summaries_batch(
            ids,
            summarizer,
            user.google_id,
            batch_size=batch_size
        )
        
        # If we have no successful summaries, handle different error cases
        if not result['summaries']:
            if result['missing_emails'] and not result['failed_summaries']:
                # Only missing emails, no generation failures
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Emails not found: {result['missing_emails']}"
                )
            elif result['failed_summaries'] and not result['missing_emails']:
                # Only generation failures, no missing emails
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Failed to generate summaries for emails: {result['failed_summaries']}"
                )
            else:
                # Both missing emails and generation failures
                error_details = {
                    "missing_emails": result['missing_emails'],
                    "failed_summaries": result['failed_summaries']
                }
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No summaries could be generated: {error_details}"
                )
        
        # If we have some successful summaries but also some failures, log a warning
        if result['missing_emails'] or result['failed_summaries']:
            logger.warning(
                f"Partial success for user {user.google_id}: "
                f"{len(result['summaries'])} successful, "
                f"{len(result['missing_emails'])} missing, "
                f"{len(result['failed_summaries'])} failed"
            )
            
        return result['summaries']
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error retrieving/generating summaries by IDs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve email summaries: {str(e)}"
        )

@router.get(
    "/", 
    response_model=List[SummarySchema],
    summary="Get user's email summaries",
    description="Retrieves summaries for the current user's emails with pagination, filtering, and regeneration options"
)
async def get_summaries(
    # Parameters for regeneration behavior (from old '/' endpoint)
    refresh: bool = Query(False, description="Force regeneration of summaries"),
    auto_generate: bool = Query(True, description="Auto-generate missing summaries"),
    
    # Parameters for pagination and sorting (from old '/all' endpoint)
    skip: int = Query(0, ge=0, description="Number of summaries to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of summaries to return"),
    sort_by: str = Query("generated_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort direction (asc or desc)"),
    
    # Service dependencies
    summarizer: AdaptiveSummarizer[EmailSchema] = Depends(get_summarizer),
    summary_service: SummaryService = Depends(get_summary_service),
    user: UserSchema = Depends(get_current_user),
    
    # Flag to control behavior
    fetch_all_emails: bool = Query(False, description="If true, fetches and processes all user emails; if false, uses pagination on existing summaries")
):
    """
    Get summaries for the current user with flexible options.
    
    This endpoint combines the functionality of the previous '/' and '/all' endpoints:
    - When fetch_all_emails=True: Fetches all user emails and generates summaries (former '/' behavior)
    - When fetch_all_emails=False: Returns paginated existing summaries (former '/all' behavior)
    
    Args:
        refresh: Whether to force regeneration of summaries (only applies when fetch_all_emails=True)
        auto_generate: Whether to automatically generate missing summaries (only applies when fetch_all_emails=True)
        skip: Number of summaries to skip for pagination
        limit: Maximum number of summaries to return
        sort_by: Field to sort by
        sort_order: Sort direction ("asc" or "desc")
        summarizer: The summarizer implementation to use
        summary_service: The summary service for data operations
        user: Current authenticated user
        fetch_all_emails: Controls whether to fetch and process all emails or just paginate existing summaries
        
    Returns:
        List[SummarySchema]: List of summaries
        
    Raises:
        HTTPException: If summary retrieval or generation fails
    """
    try:
        # If fetch_all_emails is True, use the old "/" endpoint behavior
        if fetch_all_emails:
            # Fetch emails using the proper instanced service
            email_service = get_email_service()
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
        
        # Otherwise, use the old "/all" endpoint behavior for pagination of existing summaries
        else:
            return await summary_service.get_summaries(
                skip=skip,
                limit=limit,
                sort_by=sort_by,
                sort_order=sort_order,
                google_id=user.google_id
            )
            
    except Exception as e:
        # Log the full error for debugging
        logger.error(f"Error processing summaries: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process email summaries"
        )

@router.get(
    "/recent/{days}", 
    response_model=List[SummarySchema],
    summary="Get recent summaries",
    description="Retrieves summaries generated within recent days"
)
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
