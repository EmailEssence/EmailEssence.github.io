# app/utils/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum
from typing import Optional
from pydantic import ConfigDict

class SummarizerProvider(str, Enum):
    OPENAI = "openai" # Currently Best option 
    GOOGLE = "gemini"  
    OPENROUTER = "openrouter"
    # TODO: Add DeepSeek
    LOCAL = "local"

    @classmethod
    def default(cls) -> "SummarizerProvider":
        return cls.OPENAI


class ProviderModel(str, Enum):
    # OpenAI Models
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    
    # Gemini Models
    GEMINI_2_FLASH_LITE = "gemini-2.0-flash-lite-preview-02-05"
    GEMINI_2_FLASH = "gemini-2.0-flash-001"
    
    # TODO: Check for updates to flash_lite!

    # OpenRouter Models
    LLAMA_4_SCOUT = "meta-llama/llama-4-scout:free"
    LLAMA_4_MAVERICK = "meta-llama/llama-4-maverick:free"
    GEMMA_3_27B_IT = "google/gemma-3-27b-it:free"


    # DeepSeek Models TODO: UNIMPLEMENTED

    @classmethod
    def default_for_provider(cls, provider: SummarizerProvider) -> "ProviderModel":
        """Get the default model for a given provider"""
        defaults = {
            SummarizerProvider.OPENAI: cls.GPT_4O_MINI,
            SummarizerProvider.GOOGLE: cls.GEMINI_2_FLASH_LITE,
            SummarizerProvider.OPENROUTER: cls.LLAMA_4_SCOUT,
            SummarizerProvider.LOCAL: cls.GEMINI_2_FLASH_LITE,  # Fallback to OpenAI
        }


        return defaults.get(provider, cls.GPT_4O_MINI)

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
    openai_api_key: str
    google_api_key: str | None = None
    deepseek_api_key: str | None = None
    gemini_api_key: str | None = None
    openrouter_api_key: str | None = None
    # Summarizer settings
    summarizer_provider: SummarizerProvider = SummarizerProvider.default()
    summarizer_model: ProviderModel = ProviderModel.default_for_provider(summarizer_provider)
    summarizer_batch_threshold: int = 10
    summarizer_prompt_version: PromptVersion = PromptVersion.latest()
    
    model_config = ConfigDict(env_file=".env", use_enum_values=True)
        
@lru_cache()
def get_settings() -> Settings:
    return Settings()