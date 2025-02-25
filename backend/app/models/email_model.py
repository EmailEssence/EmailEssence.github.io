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
