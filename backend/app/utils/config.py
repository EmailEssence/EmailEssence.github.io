# app/utils/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    
    # Email
    email_account: str
    
    # Database
    mongo_uri: str
    
    # Environment
    environment: str = "development"

    class Config:
        env_file = ".env"
        
@lru_cache()
def get_settings() -> Settings:
    return Settings()