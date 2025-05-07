"""
Email models for Email Essence.

This module defines the Pydantic models used for email-related operations.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from typing import List, Optional, Dict

class EmailSchema(BaseModel):
    """
    Schema for email data storage and retrieval.
    """
    google_id: str  # Google User ID for consistent user identification
    email_id: str
    sender: str
    recipients: List[str]
    subject: str
    body: str
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    category: str = "uncategorized"
    is_read: bool = False
    
    model_config = ConfigDict(frozen=True)  # Using new Pydantic v2 syntax for immutability
    
    @classmethod
    def from_dict(cls, data: Dict) -> "EmailSchema":
        """
        Create an EmailSchema instance from a dictionary.
        
        Args:
            data: Dictionary containing email data
            
        Returns:
            EmailSchema: New instance
        """
        if isinstance(data, cls):
            return data
        return cls(**data)
    
    def to_dict(self) -> Dict:
        """
        Convert email to a dictionary for MongoDB storage.
        
        Returns:
            Dict: Dictionary representation of this email
        """
        return self.model_dump()  # Using Pydantic v2 method

class EmailResponse(BaseModel):
    """Response model for email listing endpoints"""
    emails: List[EmailSchema]
    total: int
    has_more: bool
    debug_info: dict

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