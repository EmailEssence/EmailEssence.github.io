
from typing import List
from fastapi import APIRouter, HTTPException

from services.email_service import fetch_emails
from services.summarization_service import summarize_emails

from backend.app.models.summary_model import EmailSummary
from backend.app.models.email_model import Email

from starlette.concurrency import run_in_threadpool

router = APIRouter()

# Retrieve all summaries
@router.get("/", response_model=List[EmailSummary])
async def summarize_emails_endpoint():
    try:
        emails_data = await run_in_threadpool(fetch_emails)
        emails = [Email(**email_dict) for email_dict in emails_data]

        summaries = summarize_emails(emails)
        return summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Retrieve a specific summary
# @router.get("/{id}", response_model=Summary)

# Create a new summary
# @router.post("/", response_model=Summary)

# Delete a specific summary
# @router.delete("/{id}")