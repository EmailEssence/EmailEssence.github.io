from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from typing import List, Optional

class EmailSchema(BaseModel):
    user_id: str  
    email_id: str
    sender: str
    recipients: List[str]
    subject: str
    body: str
    received_at: Optional[datetime] = datetime.now(timezone.utc)
    category: Optional[str] = "uncategorized"
    is_read: Optional[bool] = False

class ReaderViewResponse(BaseModel):
    """Response model for reader view endpoint"""
    email_id: str
    subject: str
    reader_content: str
    content_type: str
    is_processed: bool
    original_length: int
    processed_length: int
    
    # Factory method to create ReaderViewResponse from EmailSchema
    @classmethod
    def from_email(cls, email: EmailSchema, reader_content: str, content_type: str, 
                  is_processed: bool, original_length: int, processed_length: int):
        """Create a ReaderViewResponse from an EmailSchema"""
        return cls(
            email_id=email.email_id,
            subject=email.subject,
            reader_content=reader_content,
            content_type=content_type,
            is_processed=is_processed,
            original_length=original_length,
            processed_length=processed_length
        )