
from typing import List
from fastapi import APIRouter, HTTPException
from app.services.email_service import fetch_emails
from app.models.email_model import Email

from starlette.concurrency import run_in_threadpool

router = APIRouter()

@router.get("/", response_model=list[Email])
async def retrieve_emails():
    try:
        emails = await fetch_emails()  # This is fine now as fetch_emails handles threading internally
        for email in emails:
            email['from_'] = email.pop('from')
        return emails
    except HTTPException as he:
        raise he  # Re-raise HTTP exceptions from our service
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve emails: {str(e)}"
        )

# Retrieve a specific email
# @router.get("/{email_id}", response_model=Email)
# async def retrieve_email(email_id: int):



# Send a new email
# @router.post("/", response_model=Email)

# Mark an email as read
# @router.put("/{email_id}/read", response_model=Email)

# Delete a specific email
# @router.delete("/{email_id}")