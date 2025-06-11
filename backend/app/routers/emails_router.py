"""
Email router for Email Essence.

This module handles all email-related operations including retrieving emails,
fetching individual email details, marking emails as read, and deleting emails.
It provides a set of REST endpoints for interacting with the user's email data.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, Query, status

# Internal imports
from app.dependencies import get_current_user
from app.utils.helpers import get_logger, log_operation, standardize_error_response
from app.models.email_models import EmailResponse, EmailSchema, ReaderViewResponse
from app.models.user_models import UserSchema
from app.services.database.factories import get_email_service
from app.services.email_service import EmailService

# -------------------------------------------------------------------------
# Router Configuration
# -------------------------------------------------------------------------

router = APIRouter()
logger = get_logger(__name__, 'router')

# -------------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------------

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
    user: UserSchema = Depends(get_current_user)
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
        log_operation(logger, 'debug', f"Email retrieval request with refresh={refresh}", extra={"params": debug_info["request_params"]})
        log_operation(logger, 'debug', f"Google ID for email retrieval: {user.google_id}")
        
        emails, total, service_debug_info = await email_service.fetch_emails(
            google_id=user.google_id,
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
        log_operation(logger, 'info', f"Retrieved {len(emails)} emails out of {total} total")
        
        return EmailResponse(
            emails=emails,
            total=total,
            has_more=(skip + len(emails)) < total,
            debug_info=debug_info
        )
        
    except Exception as e:
        raise standardize_error_response(e, "retrieve emails")

@router.get(
    "/{email_id}", 
    response_model=EmailSchema,
    summary="Get email by ID",
    description="Retrieves a specific email by its ID"
)
async def retrieve_email(
    email_id: str, 
    email_service: EmailService = Depends(get_email_service),
    user: UserSchema = Depends(get_current_user)
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
    email = await email_service.get_email(email_id, user.google_id)
    if not email:
        raise standardize_error_response(
            Exception("Email not found"), 
            "get email", 
            email_id
        )
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
    user: UserSchema = Depends(get_current_user)
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
    updated_email = await email_service.mark_email_as_read(email_id, user.google_id)
    if not updated_email:
        raise standardize_error_response(
            Exception("Email not found"), 
            "mark email as read", 
            email_id
        )
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
    user: UserSchema = Depends(get_current_user)
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
    success = await email_service.delete_email(email_id, user.google_id)
    if not success:
        raise standardize_error_response(
            Exception("Email not found"), 
            "delete email", 
            email_id
        )
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
    user: UserSchema = Depends(get_current_user)
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
        
        reader_content = await email_service.get_email_reader_view(email_id, user.google_id)
        
        if not reader_content:
            raise standardize_error_response(
                Exception("Email not found"), 
                "get email reader view", 
                email_id
            )
            
        return reader_content
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise standardize_error_response(e, "generate reader view", email_id)