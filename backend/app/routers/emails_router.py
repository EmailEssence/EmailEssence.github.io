from typing import List
from fastapi import APIRouter, HTTPException
from app.services import email_service
from app.models import EmailSchema

router = APIRouter()

# Get all emails
@router.get("/", response_model=List[EmailSchema])
async def retrieve_emails():
    try:
        emails = await email_service.fetch_emails()
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve emails: {str(e)}")

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