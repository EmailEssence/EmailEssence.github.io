# app/utils/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum
from typing import Optional, List
from pydantic import ConfigDict

class SummarizerProvider(str, Enum):
    OPENAI = "openai" # Currently Best option 
    GOOGLE = "gemini"  
    OPENROUTER = "openrouter"
    LOCAL = "local"

    @classmethod
    def default(cls) -> "SummarizerProvider":
        return cls.OPENROUTER


class ProviderModel(str, Enum):
    # OpenAI Models
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    
    # Gemini Models
    GEMINI_2_FLASH_LITE = "gemini-2.0-flash-lite-preview-02-05"
    GEMINI_2_FLASH = "gemini-2.0-flash-001"

    # OpenRouter - 
    OR_GPT_4_1_NANO = "openai/gpt-4.1-nano"
    OR_MINISTRAL_8B = "mistralai/ministral-8b"
    OR_GEMINI_2_5_FLASH = "google/gemini-2.5-flash-preview"

    @classmethod
    def default_for_provider(cls, provider: SummarizerProvider) -> "ProviderModel":
        """Get the default model for a given provider"""
        defaults = {
            SummarizerProvider.OPENAI: cls.GPT_4O_MINI,
            SummarizerProvider.GOOGLE: cls.GEMINI_2_FLASH_LITE,
            SummarizerProvider.OPENROUTER: cls.OR_GPT_4_1_NANO,
            SummarizerProvider.LOCAL: cls.GPT_4O_MINI,  # Fallback to OpenAI
        }

        return defaults.get(provider, cls.GPT_4O_MINI)

    @classmethod
    def get_openrouter_fallbacks(cls) -> List["ProviderModel"]:
        """
        Get ordered list of OpenRouter models for fallback.
        The API limits the fallback list to a maximum of 3 models.
        """
        return [
            cls.OR_GPT_4_1_NANO,
            cls.OR_MINISTRAL_8B,
            cls.OR_GEMINI_2_5_FLASH,
        ]

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
    
    # Backend URLs
    backend_base_url: Optional[str] = None
    oauth_callback_url: Optional[str] = None

    # AI Providers
    openrouter_api_key: str # Required Now :)
    openai_api_key: str | None = None
    google_api_key: str | None = None
    deepseek_api_key: str | None = None
    gemini_api_key: str | None = None
     
    # Summarizer settings
    summarizer_provider: SummarizerProvider = SummarizerProvider.default()
    summarizer_model: ProviderModel = ProviderModel.default_for_provider(summarizer_provider)
    summarizer_batch_threshold: int = 10
    summarizer_prompt_version: PromptVersion = PromptVersion.latest()
    
    model_config = ConfigDict(env_file=".env", use_enum_values=True)
        
@lru_cache()
def get_settings() -> Settings:
    return Settings()