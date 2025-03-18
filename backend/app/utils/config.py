# app/utils/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum

class SummarizerProvider(str, Enum):
    OPENAI = "openai"
    GOOGLE = "gemini" # Currently Best option  
    # TODO: Add DeepSeek
    LOCAL = "local"

    @classmethod
    def default(cls) -> "SummarizerProvider":
        return cls.GOOGLE


class ProviderModel(str, Enum):
    # OpenAI Models
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    
    # Gemini Models
    GEMINI_2_FLASH_LITE = "gemini-2.0-flash-lite-preview-02-05"
    GEMINI_2_FLASH = "gemini-2.0-flash-001"
    
    # TODO: Check for updates to flash_lite!

    # DeepSeek Models TODO: UNIMPLEMENTED

    @classmethod
    def default_for_provider(cls, provider: SummarizerProvider) -> "ProviderModel":
        """Get the default model for a given provider"""
        defaults = {
            SummarizerProvider.OPENAI: cls.GPT_4O_MINI,
            SummarizerProvider.GOOGLE: cls.GEMINI_2_FLASH_LITE,
            SummarizerProvider.LOCAL: cls.GEMINI_2_FLASH_LITE,  # Fallback to OpenAI
        }


        return defaults.get(provider, cls.GEMINI_2_FLASH_LITE)

class PromptVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"
    # Add new versions as needed

    @classmethod
    def latest(cls) -> "PromptVersion":
        return cls.V1

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

    # AI Providers
    openai_api_key: str
    google_api_key: str | None = None
    deepseek_api_key: str | None = None
    gemini_api_key: str | None = None
    
    # Summarizer settings
    summarizer_provider: SummarizerProvider = SummarizerProvider.default()
    summarizer_model: ProviderModel = ProviderModel.default_for_provider(summarizer_provider)
    summarizer_batch_threshold: int = 10
    summarizer_prompt_version: PromptVersion = PromptVersion.latest()
    

    class Config:
        env_file = ".env"
        use_enum_values = True
        
@lru_cache()
def get_settings() -> Settings:
    return Settings()