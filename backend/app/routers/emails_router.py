"""
Email router for Email Essence.

This module handles all email-related operations including retrieving emails,
fetching individual email details, marking emails as read, and deleting emails.
It provides a set of REST endpoints for interacting with the user's email data.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from pydantic import BaseModel
from app.services import EmailService
from app.models import EmailSchema, ReaderViewResponse
from functools import lru_cache
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import get_credentials_from_token
from app.routers.user_router import get_current_user_info, get_current_user

router = APIRouter()

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

# -------------------------------------------------------------------------
# Service dependency injection for better scalability
# -------------------------------------------------------------------------

@lru_cache()
def get_email_service() -> EmailService:
    """
    Factory function that returns an EmailService instance.
    Using lru_cache for efficiency so we don't create a new instance for every request.
    """
    return EmailService()

class EmailResponse(BaseModel):
    """Response model for email listing endpoints"""
    emails: List[EmailSchema]
    total: int
    has_more: bool
    debug_info: dict

@router.get(
    "/", 
    response_model=EmailResponse,
    summary="List emails",
    description="Retrieves emails with filtering, sorting, and pagination options"
)
async def retrieve_emails(
    skip: int = Query(default=0, ge=0, description="Number of emails to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of emails to return"),
    unread_only: bool = Query(default=False, description="Filter for unread emails only"),
    category: Optional[str] = Query(default=None, description="Filter by email category"),
    search: Optional[str] = Query(default=None, description="Search in subject and body"),
    sort_by: str = Query(default="received_at", enum=["received_at", "sender", "subject"]),
    sort_order: str = Query(default="desc", enum=["asc", "desc"]),
    refresh: bool = Query(default=False, description="Whether to refresh emails from IMAP first"),
    email_service: EmailService = Depends(get_email_service),
    user: dict = Depends(get_current_user)
):
    """
    Retrieve emails with filtering, sorting, and pagination options.
    
    This endpoint serves as the main method for fetching emails from the system.
    It can optionally refresh from IMAP first before returning results.
    
    Args:
        skip: Number of emails to skip (for pagination)
        limit: Maximum number of emails to return
        unread_only: Whether to only return unread emails
        category: Filter emails by category
        search: Search term to filter emails by subject and body
        sort_by: Field to sort results by
        sort_order: Direction to sort results
        refresh: Whether to refresh emails from IMAP before returning
        email_service: Email service instance
        user: Current authenticated user
        
    Returns:
        EmailResponse: List of emails with pagination info
        
    Raises:
        HTTPException: If email retrieval fails
    """
    debug_info = {
        "request_params": {
            "skip": skip,
            "limit": limit,
            "unread_only": unread_only,
            "category": category,
            "search": search,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "refresh": refresh
        }
    }
    
    try:
        # Log request parameters
        logger.debug(f"Email retrieval request with refresh={refresh}", extra={"params": debug_info["request_params"]})
        
        # Get the user ID from the authenticated user
        user_id = str(user.get("_id", user.get("google_id")))
        logger.debug(f"User ID for email retrieval: {user_id}")
        
        emails, total, service_debug_info = await email_service.fetch_emails(
            user_id=user_id,
            skip=skip,
            limit=limit,
            unread_only=unread_only,
            category=category,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            refresh=refresh
        )
        
        # Combine debug info
        debug_info.update(service_debug_info)
        logger.info(f"Retrieved {len(emails)} emails out of {total} total")
        
        return EmailResponse(
            emails=emails,
            total=total,
            has_more=(skip + len(emails)) < total,
            debug_info=debug_info
        )
        
    except Exception as e:
        error_msg = f"Failed to retrieve emails: {str(e)}"
        logger.exception(error_msg)  # This logs the full stack trace
        raise HTTPException(status_code=500, detail=error_msg)

@router.get(
    "/{email_id}", 
    response_model=EmailSchema,
    summary="Get email by ID",
    description="Retrieves a specific email by its ID"
)
async def retrieve_email(
    email_id: str, 
    email_service: EmailService = Depends(get_email_service),
    user: dict = Depends(get_current_user)
):
    """
    Retrieve a specific email by its ID.
    
    Args:
        email_id: Unique identifier for the email
        email_service: Email service instance
        user: Current authenticated user
        
    Returns:
        EmailSchema: The requested email
        
    Raises:
        HTTPException: If email not found
    """
    user_id = user.get("_id", user.get("google_id"))
    email = await email_service.get_email(email_id, user_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@router.put(
    "/{email_id}/read", 
    response_model=EmailSchema,
    summary="Mark email as read",
    description="Marks a specific email as read"
)
async def mark_email_as_read(
    email_id: str,
    email_service: EmailService = Depends(get_email_service),
    user: dict = Depends(get_current_user)
):
    """
    Mark a specific email as read.
    
    Args:
        email_id: Unique identifier for the email
        email_service: Email service instance
        user: Current authenticated user
        
    Returns:
        EmailSchema: The updated email
        
    Raises:
        HTTPException: If email not found or update fails
    """
    user_id = user.get("_id", user.get("google_id"))
    updated_email = await email_service.mark_email_as_read(email_id, user_id)
    if not updated_email:
        raise HTTPException(status_code=404, detail="Email not found")
    return updated_email

@router.delete(
    "/{email_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete email",
    description="Deletes a specific email"
)
async def delete_email(
    email_id: str,
    email_service: EmailService = Depends(get_email_service),
    user: dict = Depends(get_current_user)
):
    """
    Delete a specific email.
    
    Args:
        email_id: Unique identifier for the email
        email_service: Email service instance
        user: Current authenticated user
        
    Returns:
        None
        
    Raises:
        HTTPException: If email not found or deletion fails
    """
    user_id = user.get("_id", user.get("google_id"))
    success = await email_service.delete_email(email_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"message": "Email deleted successfully"}

@router.get(
    "/{email_id}/reader-view", 
    response_model=ReaderViewResponse,
    summary="Get email reader view",
    description="Returns a reader-friendly version of an email"
)
async def get_email_reader_view(
    email_id: str,
    email_service: EmailService = Depends(get_email_service),
    user: dict = Depends(get_current_user)
):
    """
    Get a reader-friendly version of an email.
    
    Args:
        email_id: Unique identifier for the email
        email_service: Email service instance
        user: Current authenticated user
        
    Returns:
        ReaderViewResponse: Reader-friendly version of the email
        
    Raises:
        HTTPException: If email not found or processing fails
    """
    try:
        logger.debug(f"Reader view requested for email {email_id}")
        
        user_id = user.get("_id", user.get("google_id"))
        reader_content = await email_service.get_email_reader_view(email_id, user_id)
        
        if not reader_content:
            raise HTTPException(status_code=404, detail="Email not found")
            
        return reader_content
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        error_msg = f"Failed to generate reader view: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)