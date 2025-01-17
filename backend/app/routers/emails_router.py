
from typing import List
from fastapi import APIRouter, HTTPException
from services.email_service import fetch_emails
from backend.app.models.email_model import Email

from starlette.concurrency import run_in_threadpool

router = APIRouter()

@router.get("/", response_model=list[Email])
async def retrieve_emails():
    try:
        emails = await run_in_threadpool(fetch_emails)
        # Adjust key name 'from_' in models to 'from' from fetch_emails
        for email in emails:
            email['from_'] = email.pop('from')
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve a specific email
# @router.get("/{email_id}", response_model=Email)
# async def retrieve_email(email_id: int):



# Send a new email
# @router.post("/", response_model=Email)

# Mark an email as read
# @router.put("/{email_id}/read", response_model=Email)

# Delete a specific email
# @router.delete("/{email_id}")