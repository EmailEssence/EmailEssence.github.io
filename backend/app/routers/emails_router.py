from typing import List
from fastapi import APIRouter, HTTPException
from app.services import email_service
from app.models.email_model import Email

router = APIRouter()

# Get all emails
@router.get("/", response_model=List[Email])
async def retrieve_emails():
    try:
        emails = await email_service.fetch_emails()
        for email in emails:
            email["from_"] = email.pop("from", None)  # Rename for response
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve emails: {str(e)}")

# Get a single email by ID
@router.get("/{email_id}", response_model=Email)
async def retrieve_email(email_id: str):
    email = await email_service.fetch_email(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email["from_"] = email.pop("from", None)
    return email

# Insert a new email
@router.post("/", response_model=Email)
async def create_email(email: Email):
    try:
        inserted_email = await email_service.insert_email(email)
        inserted_email["from_"] = inserted_email.pop("from", None)
        return inserted_email
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert email: {str(e)}")

# Mark an email as read
@router.put("/{email_id}/read", response_model=Email)
async def mark_email_as_read(email_id: str):
    updated_email = await email_service.mark_email_as_read(email_id)
    if not updated_email:
        raise HTTPException(status_code=404, detail="Email not found")
    updated_email["from_"] = updated_email.pop("from", None)
    return updated_email

# Delete an email
@router.delete("/{email_id}")
async def delete_email(email_id: str):
    success = await email_service.delete_email(email_id)
    if not success:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"message": "Email deleted successfully"}