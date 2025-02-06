# tests/api/conftest.py
import pytest
from typing import Generator
from unittest.mock import Mock, patch

@pytest.fixture
def mock_email_response():
    """
    Mock email data for testing email endpoints
    """
    return [{
        "id": 1,
        "from": "sender@example.com",
        "subject": "Test Subject",
        "body": "Test email body content"
    }]

@pytest.fixture
def mock_fetch_emails(mock_email_response):
    """
    Mock the fetch_emails function from email_service
    """
    with patch("app.services.email_service.fetch_emails") as mock:
        mock.return_value = mock_email_response
        yield mock

@pytest.fixture
def mock_imap_client():
    """
    Mock IMAP client for testing email operations
    """
    with patch("app.services.email_service.IMAPClient") as mock:
        client_instance = Mock()
        mock.return_value.__enter__.return_value = client_instance
        yield client_instance