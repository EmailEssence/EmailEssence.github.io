# tests/conftest.py
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

from typing import Generator
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import all fixtures from constants.py
# This makes all fixtures available to all tests automatically
from app.tests.constants import (
    mock_email_message,
    mock_email_schema,
    mock_summary,
    mock_db,
    mock_db_cursor,
    mock_empty_db_cursor,
    mock_imap_client,
    mock_credentials,
    mock_threadpool,
    mock_fetch_emails,
    mock_empty_fetch_emails,
    mock_error_fetch_emails
)

# Base application fixture
@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """
    Create a FastAPI test application with test settings.
    """
    from main import app
    from app.tests.test_config import override_get_settings
    from app.utils.config import get_settings
    
    # Override the get_settings dependency with test settings
    app.dependency_overrides[get_settings] = override_get_settings
    
    return app

# TestClient fixture
@pytest.fixture(scope="module")
def test_client(test_app: FastAPI) -> Generator:
    """
    Create a TestClient instance for making test requests.
    """
    with TestClient(test_app) as client:
        yield client

def load_env_file(env_file: str) -> None:
    """
    Load environment variables from a file in the tests directory.
    """
    env_path = Path(__file__).parent / env_file
    if env_path.exists():
        load_dotenv(env_path)
    else:
        print(f"Warning: Environment file {env_file} not found in tests directory, using default mock values")

# Note: We now have environment variables set at the root conftest level,
# so this is mostly for local development where you might want to use .env.test
@pytest.fixture(scope="session", autouse=True)
def test_settings():
    """
    Configure test environment settings.
    Automatically loads test environment on session start.
    If .env.test doesn't exist, uses mock values suitable for testing.
    """
    # Try to load test-specific environment variables
    load_env_file('.env.test')
    
    # Environment variables are now set in the root conftest.py
    # This fixture remains for backward compatibility
    return {
        "TESTING": True,
        "EMAIL_ACCOUNT": os.getenv("EMAIL_ACCOUNT", "test@example.com"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "test_key_123"),
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", "test_client_id"),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", "test_client_secret"),
        "MONGO_URI": os.getenv("MONGO_URI", "mongodb://localhost:27017/test_db")
    }