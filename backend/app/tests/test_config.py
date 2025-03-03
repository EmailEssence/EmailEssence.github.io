"""
Test configuration module that overrides the main application settings for testing.
"""
from app.utils.config import Settings, SummarizerProvider, get_settings
import os
from functools import lru_cache

class TestSettings(Settings):
    """
    Test-specific settings that override the main application settings.
    This uses the TEST_* prefixed environment variables.
    """
    # Override with test values
    google_client_id: str = os.getenv("TEST_GOOGLE_CLIENT_ID", "test-client-id")
    google_client_secret: str = os.getenv("TEST_GOOGLE_CLIENT_SECRET", "test-client-secret")
    email_account: str = os.getenv("TEST_EMAIL_ACCOUNT", "test@example.com")
    mongo_uri: str = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017/test_db")
    openai_api_key: str = os.getenv("TEST_OPENAI_API_KEY", "sk-test-key-123456789")
    deepseek_api_key: str | None = os.getenv("TEST_DEEPSEEK_API_KEY")
    gemini_api_key: str | None = os.getenv("TEST_GEMINI_API_KEY")
    
    # Set environment to testing
    environment: str = "testing"
    
    # Summarizer settings
    summarizer_provider: SummarizerProvider = SummarizerProvider(
        os.getenv("TEST_SUMMARIZER_PROVIDER", SummarizerProvider.OPENAI)
    )
    summarizer_model: str = os.getenv("TEST_SUMMARIZER_MODEL", "gpt-4o-mini")
    summarizer_batch_threshold: int = int(os.getenv("TEST_SUMMARIZER_BATCH_THRESHOLD", "10"))
    
    class Config:
        env_file = ".env.test"
        use_enum_values = True

@lru_cache()
def get_test_settings() -> TestSettings:
    """
    Returns cached test settings.
    This should be used in place of get_settings() during tests.
    """
    return TestSettings()

# Function to patch the get_settings to return test settings
def override_get_settings():
    """
    Returns the test settings function.
    Use this with fastapi.dependency_overrides to replace the real settings
    with test settings during tests.
    """
    return get_test_settings 