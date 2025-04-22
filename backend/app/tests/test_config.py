"""
Test configuration module for test environment settings
"""
from app.utils.config import Settings, SummarizerProvider
import os
from functools import lru_cache
from pydantic import ConfigDict

class MockSettings(Settings):
    """
    Test-specific settings that override the main application settings.
    This uses environment variables set in the root conftest.py
    """
    # Override with test values - no TEST_ prefix since we directly set the variables
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "test-client-id")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "test-client-secret")
    email_account: str = os.getenv("EMAIL_ACCOUNT", "test@example.com")
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/test_db")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "sk-test-key-123456789")
    deepseek_api_key: str | None = os.getenv("DEEPSEEK_API_KEY")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    
    # Set environment to testing
    environment: str = "testing"
    
    # Summarizer settings
    summarizer_provider: SummarizerProvider = SummarizerProvider(
        os.getenv("SUMMARIZER_PROVIDER", SummarizerProvider.OPENAI)
    )
    summarizer_model: str = os.getenv("SUMMARIZER_MODEL", "gpt-4o-mini")
    summarizer_batch_threshold: int = int(os.getenv("SUMMARIZER_BATCH_THRESHOLD", "10"))
    
    model_config = ConfigDict(env_file=".env.test", use_enum_values=True)

@lru_cache()
def get_test_settings() -> MockSettings:
    """
    Returns cached test settings.
    This should be used in place of get_settings() during tests.
    """
    return MockSettings()

# Function to patch the get_settings to return test settings
def override_get_settings():
    """
    Function to override the get_settings dependency.
    Used in app.dependency_overrides during testing.
    """
    return get_test_settings() 