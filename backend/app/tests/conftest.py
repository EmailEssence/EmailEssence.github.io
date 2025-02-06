# tests/conftest.py
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

from typing import Generator
from fastapi.testclient import TestClient
from fastapi import FastAPI

from main import app  # main FastAPI application

# Base application fixture
@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """
    Create a fresh FastAPI application for testing.
    """
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
    """Load environment variables from specified file"""
    env_path = Path(__file__).parent / env_file
    if env_path.exists():
        load_dotenv(env_path)
    else:
        raise FileNotFoundError(f"Environment file {env_file} not found in tests directory")

@pytest.fixture(scope="session", autouse=True)
def test_settings():
    """
    Configure test environment settings.
    Automatically loads test environment on session start.
    """
    # Load test-specific environment variables
    load_env_file('.env.test')
    
    return {
        "TESTING": True,
        "EMAIL_ACCOUNT": os.getenv("TEST_EMAIL_ACCOUNT", "test@example.com"),
        "OPENAI_API_KEY": os.getenv("TEST_OPENAI_API_KEY", "test_key_123"),
        "GOOGLE_CLIENT_ID": os.getenv("TEST_GOOGLE_CLIENT_ID", "test_client_id"),
        "GOOGLE_CLIENT_SECRET": os.getenv("TEST_GOOGLE_CLIENT_SECRET", "test_client_secret")
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
