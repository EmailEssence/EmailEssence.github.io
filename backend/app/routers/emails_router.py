import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from app.services import EmailService
from app.models import EmailSchema, ReaderViewResponse
from functools import lru_cache

router = APIRouter()

# Configure logging with format and level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

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
    emails: List[EmailSchema]
    total: int
    has_more: bool
    debug_info: dict

@router.get("/", response_model=EmailResponse)
async def retrieve_emails(
    skip: int = Query(default=0, ge=0, description="Number of emails to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of emails to return"),
    unread_only: bool = Query(default=False, description="Filter for unread emails only"),
    category: Optional[str] = Query(default=None, description="Filter by email category"),
    search: Optional[str] = Query(default=None, description="Search in subject and body"),
    sort_by: str = Query(default="received_at", enum=["received_at", "sender", "subject"]),
    sort_order: str = Query(default="desc", enum=["asc", "desc"]),
    refresh: bool = Query(default=False, description="Whether to refresh emails from IMAP first"),
    email_service: EmailService = Depends(get_email_service)
):
    """
    Retrieve emails with filtering, sorting, and pagination options.
    
    This endpoint serves as the main method for fetching emails from the system.
    It can optionally refresh from IMAP first before returning results.
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
        logger.debug("Email retrieval request", extra={"params": debug_info["request_params"]})
        
        emails, total, service_debug_info = await email_service.fetch_emails(
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

# Get a single email by ID
@router.get("/{email_id}", response_model=EmailSchema)
async def retrieve_email(
    email_id: str, 
    email_service: EmailService = Depends(get_email_service)
):
    """
    Retrieve a single email by its unique ID.
    """
    email = await email_service.get_email(email_id)  # Changed from fetch_email to get_email
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

# Mark an email as read
@router.put("/{email_id}/read", response_model=EmailSchema)
async def mark_email_as_read(
    email_id: str,
    email_service: EmailService = Depends(get_email_service)
):
    """
    Mark an email as read.
    
    Updates the is_read flag to true for the specified email.
    """
    updated_email = await email_service.mark_email_as_read(email_id)
    if not updated_email:
        raise HTTPException(status_code=404, detail="Email not found")
    return updated_email

# Delete an email
@router.delete("/{email_id}")
async def delete_email(
    email_id: str,
    email_service: EmailService = Depends(get_email_service)
):
    """
    Delete an email by ID.
    
    Completely removes the email from the database.
    """
    success = await email_service.delete_email(email_id)
    if not success:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"message": "Email deleted successfully"}

@router.get("/{email_id}/reader-view", response_model=ReaderViewResponse)
async def get_email_reader_view(
    email_id: str,
    email_service: EmailService = Depends(get_email_service)
):
    """
    Get a reader-view friendly version of the email content.
    
    This endpoint processes the email content to provide a clean,
    readable version focusing on the main content.
    """
    try:
        logger.debug(f"Reader view requested for email {email_id}")
        
        reader_content = await email_service.get_email_reader_view(email_id)
        
        if not reader_content:
            raise HTTPException(status_code=404, detail="Email not found")
            
        return reader_content
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        error_msg = f"Failed to generate reader view: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)