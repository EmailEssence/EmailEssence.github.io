from pydantic import BaseModel, Field, ConfigDict

class EmailSummary(BaseModel):
    email_id: int
    summary: str