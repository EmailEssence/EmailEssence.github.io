"""
Fixtures for API endpoint tests.

This module provides fixtures specific to testing the API routes.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone
from main import app

# Import mock_db from unit tests
from app.tests.unit.email.conftest import mock_db

@pytest.fixture
def test_client():
    """
    Creates a FastAPI TestClient for testing API endpoints.
    """
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_email_schema():
    """
    Creates a mock email schema for testing API responses.
    
    Returns a dictionary that resembles an EmailSchema object.
    """
    from app.models import EmailSchema
    
    # Create a mock EmailSchema with test data
    return EmailSchema(
        user_id="test_user",
        email_id="test_123",
        sender="sender@test.com",
        recipients=["recipient@test.com"],
        subject="Test Subject",
        body="This is a test email body.",
        received_at=datetime.now(timezone.utc),
        category="test",
        is_read=False
    ) 