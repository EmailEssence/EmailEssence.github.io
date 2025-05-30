from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class ThemeEnum(str, Enum):
    light = 'light'
    system = 'system'
    dark = 'dark'

class EmailSummary(BaseModel):
    summariesInInbox: bool
    emailFetchInterval: int = Field(alias='emailFetchInterval')
    theme: ThemeEnum
    
    model_config = ConfigDict()  # Allow mutations for settings