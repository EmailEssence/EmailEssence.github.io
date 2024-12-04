from pydantic import BaseModel

class Email(BaseModel):
    id: int
    from_: str
    subject: str
    body: str
