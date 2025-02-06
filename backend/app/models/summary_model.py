from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from typing import List, Optional

class SummarySchema(BaseModel):
    email_id: str
    summary_text: str
    keywords: List[str]
    generated_at: Optional[datetime] = datetime.now(timezone.utc) 
    class Config:
        frozen = True # Immutable!