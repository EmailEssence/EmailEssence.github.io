# tests/conftest.py
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

from typing import Generator
from fastapi.testclient import TestClient
from fastapi import FastAPI

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

@pytest.fixture(scope="session", autouse=True)
def test_settings():
    """
    Configure test environment settings.
    Automatically loads test environment on session start.
    If .env.test doesn't exist, uses mock values suitable for testing.
    """
    # Try to load test-specific environment variables
    load_env_file('.env.test')
    
    # Set environment variables with mock values if not present
    test_env_vars = {
        "TEST_EMAIL_ACCOUNT": "test@example.com",
        "TEST_OPENAI_API_KEY": "sk-test-key-123456789",
        "TEST_GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
        "TEST_GOOGLE_CLIENT_SECRET": "test-client-secret-123456",
        "TEST_MONGO_URI": "mongodb://localhost:27017/test_db"
    }
    
    for key, value in test_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    return {
        "TESTING": True,
        "EMAIL_ACCOUNT": os.getenv("TEST_EMAIL_ACCOUNT", "test@example.com"),
        "OPENAI_API_KEY": os.getenv("TEST_OPENAI_API_KEY", "test_key_123"),
        "GOOGLE_CLIENT_ID": os.getenv("TEST_GOOGLE_CLIENT_ID", "test_client_id"),
        "GOOGLE_CLIENT_SECRET": os.getenv("TEST_GOOGLE_CLIENT_SECRET", "test_client_secret"),
        "MONGO_URI": os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017/test_db")
    }

# Mock Credentials fixture
@pytest.fixture(scope="function")
def mock_credentials():
    """
    Mock OAuth credentials for testing.
    """
    return {
        "token": "test_token",
        "refresh_token": "test_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "scopes": ["https://mail.google.com/"]
    }
