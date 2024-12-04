# uvicorn main:app --reload

from fastapi import FastAPI, HTTPException
from typing import List
from models import Email, EmailSummary
from email_client import fetch_emails
from email_client import summarize_emails
from starlette.concurrency import run_in_threadpool

app = FastAPI()

@app.get('/emails/', response_model=List[Email])
async def emails_endpoint():
    try:
        emails = await run_in_threadpool(fetch_emails)
        # Adjust key name 'from_' in models to 'from' from fetch_emails
        for email in emails:
            email['from_'] = email.pop('from')
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/emails/summarize', response_model=List[EmailSummary])
async def summarize_emails_endpoint():
    try:
        emails_data = await run_in_threadpool(fetch_emails)
        emails = [Email(**email_dict) for email_dict in emails_data]

        summaries = summarize_emails(emails)
        return summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))