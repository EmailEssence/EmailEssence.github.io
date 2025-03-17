import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services import email_service
from app.models import EmailSchema

router = APIRouter()

# # Get all emails
# @router.get("/", response_model=List[EmailSchema])
# async def retrieve_emails():
#     try:
#         emails = await email_service.fetch_emails()
#         return emails
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to retrieve emails: {str(e)}")

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
    refresh: bool = Query(default=False, description="Whether to refresh emails from IMAP first")
):
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


# // Get first 20 unread emails
# GET /emails?unread_only=true&limit=20

# // Get next page of emails
# GET /emails?skip=20&limit=20

# // Search emails with pagination
# GET /emails?search=important&skip=0&limit=50

# // Get newest emails first
# GET /emails?sort_by=received_at&sort_order=desc

# Get a single email by ID
@router.get("/{email_id}", response_model=EmailSchema)
async def retrieve_email(email_id: str):
    email = await email_service.fetch_email(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

# Insert a new email
@router.post("/", response_model=EmailSchema)
async def create_email(email: EmailSchema):
    try:
        inserted_email = await email_service.insert_email(email)
        return inserted_email
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert email: {str(e)}")

# Mark an email as read
@router.put("/{email_id}/read", response_model=EmailSchema)
async def mark_email_as_read(email_id: str):
    updated_email = await email_service.mark_email_as_read(email_id)
    if not updated_email:
        raise HTTPException(status_code=404, detail="Email not found")
    return updated_email

# Delete an email
@router.delete("/{email_id}")
async def delete_email(email_id: str):
    success = await email_service.delete_email(email_id)
    if not success:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"message": "Email deleted successfully"}