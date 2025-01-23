
from typing import List
from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from app.services import email_service, summarization_service
from app.models import Email, EmailSummary


router = APIRouter()

# Retrieve all summaries
@router.get("/", response_model=List[EmailSummary])
async def summarize_emails_endpoint():
    try:
        emails_data = await email_service.fetch_emails()
        emails = [Email(**email_dict) for email_dict in emails_data]

        summaries = summarization_service.summarize_emails(emails)
        return summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Retrieve a specific summary
# @router.get("/{id}", response_model=Summary)

# Create a new summary
# @router.post("/", response_model=Summary)

# Delete a specific summary
# @router.delete("/{id}")