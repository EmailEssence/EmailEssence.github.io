# tests/constants.py
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock
import email.message

from app.models import EmailSchema, SummarySchema, UserSchema, TokenData, PreferencesSchema

"""
Test constants fixtures
"""

# Mock data constants
EMAIL_DATA = [
    {
        "email_id": "test_1",
        "google_id": "user123",
        "sender": "test@example.com",
        "recipients": ["recipient@example.com"],
        "subject": "Test Email 1",
        "body": "This is a test email body",
        "received_at": "2023-01-01T00:00:00Z",
        "category": "inbox",
        "is_read": False
    },
    {
        "email_id": "test_2",
        "google_id": "user123",
        "sender": "another@example.com",
        "recipients": ["recipient@example.com"],
        "subject": "Test Email 2",
        "body": "This is another test email body",
        "received_at": "2023-01-02T00:00:00Z",
        "category": "inbox",
        "is_read": True
    }
]

USER_DATA = [
    {
        "google_id": "user123",
        "email": "user@example.com",
        "name": "Test User",
        "preferences": {
            "summaries": True,
            "theme": "dark",
            "fetch_frequency": "60"
        }
    }
]

TOKEN_DATA = [
    {
        "google_id": "user123",
        "token": "access_token_123",
        "refresh_token": "refresh_token_123",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
    }
]

SUMMARY_DATA = [
    {
        "email_id": "test_1",
        "google_id": "user123",
        "summary_text": "Test email summary",
        "keywords": ["test", "email"],
        "generated_at": "2023-01-01T01:00:00Z",
        "model_info": {"model": "test-model"}
    }
]

# Test data fixtures
@pytest.fixture
def mock_email_message():
    """Create a mock email.message.Message object for testing"""
    msg = email.message.Message()
    msg['Subject'] = "Test Subject"
    msg['From'] = "sender@example.com"
    msg['To'] = "recipient1@example.com, recipient2@example.com"
    msg['Date'] = datetime.now(timezone.utc)
    msg['Body'] = "This is a test email body"
    return msg

@pytest.fixture
def mock_email_schema():
    """Create a mock EmailSchema for testing"""
    return EmailSchema(**EMAIL_DATA[0])

@pytest.fixture
def mock_summary_schema():
    """Create a mock summary model for testing"""
    return SummarySchema(**SUMMARY_DATA[0])

@pytest.fixture
def mock_user():
    """Create a mock user model for testing"""
    return UserSchema(**USER_DATA[0])

@pytest.fixture(scope="function")
def mock_token_data():
    """Mock OAuth credentials for testing."""
    return TokenData(**TOKEN_DATA[0])

# @pytest.fixture
# def mock_db_cursor():
#     """Create a mock MongoDB cursor with to_list method"""
#     email_data = {
#         "user_id": "default",
#         "email_id": "1",
#         "sender": "test@example.com",
#         "recipients": ["recipient@example.com"],
#         "subject": "Test Subject",
#         "body": "Test content",
#         "received_at": datetime.now(timezone.utc),
#         "category": "uncategorized",
#         "is_read": False
#     }
    
#     mock_cursor = AsyncMock()
#     mock_cursor.to_list = AsyncMock(return_value=[email_data])
#     return mock_cursor

# @pytest.fixture
# def mock_empty_db_cursor():
#     """Create a mock MongoDB cursor that returns empty results"""
#     mock_cursor = AsyncMock()
#     mock_cursor.to_list = AsyncMock(return_value=[])
#     return mock_cursor

# @pytest.fixture
# def mock_db(mock_db_cursor):
#     """Create a mock database with properly configured cursor"""
#     mock = AsyncMock()
#     mock.emails = AsyncMock()
#     # Instead of returning the cursor directly, set it as the return value
#     # This ensures find() returns the cursor object, not a coroutine
#     mock.emails.find.return_value = mock_db_cursor
    
#     # Add other commonly used DB methods
#     email_data = {
#         "user_id": "default",
#         "email_id": "1",
#         "sender": "test@example.com",
#         "recipients": ["recipient@example.com"],
#         "subject": "Test Subject",
#         "body": "Test content",
#         "received_at": datetime.now(timezone.utc),
#         "category": "uncategorized",
#         "is_read": False
#     }
#     mock.emails.find_one = AsyncMock(return_value=email_data)
#     mock.emails.insert_one = AsyncMock(return_value=MagicMock(inserted_id="new_id"))
#     mock.emails.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
#     mock.emails.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
    
#     return mock

@pytest.fixture
def mock_imap_client():
    """Create a mock IMAP client for testing"""
    mock = MagicMock()
    
    # Configure search and fetch behavior
    mock.search.return_value = [1]
    fetch_result = {
        1: {
            b'RFC822': b'From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test Email\r\n\r\nThis is a test email body',
            b'INTERNALDATE': datetime.now()
        }
    }
    mock.fetch = MagicMock(return_value=fetch_result)
    
    # Context manager support
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)
    
    return mock

@pytest.fixture
def mock_threadpool():
    """Create a mock for the threadpool that properly handles sync functions in async context"""
    async def mock_func(func, *args, **kwargs):
        return func(*args, **kwargs)
    return AsyncMock(side_effect=mock_func)

@pytest.fixture
def mock_fetch_emails():
    """Mock the fetch_emails function for API tests"""
    # Create a standard test email object that matches EmailSchema
    test_email = {
        "user_id": "default",
        "email_id": "1",
        "sender": "test@example.com",
        "recipients": ["recipient@example.com"],
        "subject": "Test Subject",
        "body": "Test content",
        "received_at": datetime.now(timezone.utc),
        "category": "uncategorized",
        "is_read": False
    }
    
    async def mock_fetch_emails_func():
        """Async function that returns test emails data"""
        return [test_email]
    
    mock = AsyncMock()
    mock.side_effect = mock_fetch_emails_func
    return mock

@pytest.fixture
def mock_empty_fetch_emails():
    """Mock fetch_emails function that returns an empty list"""
    mock = AsyncMock(return_value=[])
    return mock

@pytest.fixture
def mock_error_fetch_emails():
    """Mock fetch_emails function that raises an exception"""
    from fastapi import HTTPException
    error_msg = "IMAP connection failed"
    mock = AsyncMock(side_effect=HTTPException(
        status_code=500, 
        detail=f"Failed to retrieve emails: {error_msg}"
    ))
    return mock