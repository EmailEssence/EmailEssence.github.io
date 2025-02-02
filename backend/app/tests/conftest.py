# tests/conftest.py
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from fastapi import FastAPI

from main import app  # Your main FastAPI application
from app.services.auth_service import get_credentials  # Your auth service
from app.services.email_service import fetch_emails  # Your email service

# Base application fixture
@pytest.fixture(scope="session")
def app() -> FastAPI:
    """
    Create a fresh FastAPI application for testing.
    """
    from app.main import app
    return app

# TestClient fixture
@pytest.fixture(scope="module")
def test_client(app: FastAPI) -> Generator:
    """
    Create a TestClient instance for making test requests.
    """
    with TestClient(app) as client:
        yield client

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

# Test environment configuration
@pytest.fixture(scope="session")
def test_settings():
    """
    Configure test environment settings.
    """
    return {
        "TESTING": True,
        "EMAIL_ACCOUNT": "test@example.com",
        "OPENAI_API_KEY": "test_key"
    }