from pydantic import BaseModel, Field, ConfigDict

class Email(BaseModel):
    id: int
    from_: str = Field(alias='from')
    subject: str
    body: str

    model_config = ConfigDict(populate_by_name=True)


class EmailSummary(BaseModel):
    email_id: int
    summary: str