# app/utils/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum
from typing import Optional

class SummarizerProvider(str, Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    LOCAL = "local"

class Settings(BaseSettings):
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    
    # Email
    email_account: str
    
    # Database
    mongo_uri: str
    
    # Environment
    environment: str = "development"
    
    # Backend URLs
    backend_base_url: Optional[str] = None
    oauth_callback_url: Optional[str] = None

    # AI Providers
    openai_api_key: str
    google_api_key: str | None = None
    
    # Summarizer settings
    summarizer_provider: SummarizerProvider = SummarizerProvider.OPENAI
    summarizer_model: str = "gpt-4o-mini"
    summarizer_batch_threshold: int = 10
    
    class Config:
        env_file = ".env"
        use_enum_values = True
        
@lru_cache()
def get_settings() -> Settings:
    return Settings()