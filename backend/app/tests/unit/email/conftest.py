"""
Common test fixtures for email service tests.

This module provides fixtures that are shared across multiple email service test files.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone
import os

from app.services.email_service import EmailService

# =============================================================================
# Common Fixtures
# =============================================================================

@pytest.fixture
def email_service():
    """Creates a fresh instance of EmailService for testing."""
    return EmailService()

@pytest.fixture
def mock_credentials():
    """Creates mock credentials for authentication tests."""
    credentials = MagicMock()
    credentials.valid = True
    credentials.token = "test_token"
    credentials.expired = False
    credentials.refresh_token = "refresh_token"
    return credentials

@pytest.fixture
def mock_email_message():
    """Creates a mock email.message.Message for parsing tests."""
    message = MagicMock()
    message.get_payload.return_value = "Test email body"
    message.get_content_type.return_value = "text/plain"
    message.get_filename.return_value = None
    message.is_multipart.return_value = False
    message.get_content_charset.return_value = "utf-8"
    
    # Add get method for headers
    message.get.side_effect = lambda x, default=None: {
        'Subject': 'Test Subject',
        'From': 'Test Sender <test@example.com>',
        'To': 'recipient@example.com'
    }.get(x, default)
    
    return message

@pytest.fixture
def multipart_message():
    """Creates a mock multipart email message."""
    msg = MagicMock()
    msg.is_multipart.return_value = True
    
    # Text part
    text_part = MagicMock()
    text_part.get_content_type.return_value = "text/plain"
    text_part.get_payload.return_value = "Plain text content"
    text_part.get_content_charset.return_value = "utf-8"
    text_part.is_multipart.return_value = False
    text_part.get_filename.return_value = None
    
    # HTML part
    html_part = MagicMock()
    html_part.get_content_type.return_value = "text/html"
    html_part.get_payload.return_value = "<div>HTML content</div>"
    html_part.get_content_charset.return_value = "utf-8"
    html_part.is_multipart.return_value = False
    html_part.get_filename.return_value = None
    
    # Attachment part
    attachment_part = MagicMock()
    attachment_part.get_content_type.return_value = "application/pdf"
    attachment_part.get_filename.return_value = "attachment.pdf"
    attachment_part.is_multipart.return_value = False
    
    # Set payload to list of parts
    msg.get_payload.return_value = [text_part, html_part, attachment_part]
    
    return msg

@pytest.fixture
def raw_email_bytes():
    """Returns a raw email in bytes format for parsing tests."""
    return (
        b'From: "Test Sender" <test@example.com>\r\n'
        b'To: "Test Recipient" <recipient@example.com>\r\n'
        b'Subject: Test Subject\r\n'
        b'Date: Tue, 17 Mar 2023 12:30:45 +0000\r\n'
        b'Message-ID: <123456789@example.com>\r\n'
        b'Content-Type: text/plain; charset="utf-8"\r\n'
        b'\r\n'
        b'This is a test email body.\r\n'
        b'With multiple lines.\r\n'
    )

@pytest.fixture
def mock_imap():
    """Creates a mock IMAPClient for IMAP tests."""
    imap = MagicMock()
    imap.fetch.return_value = {
        1: {
            b'RFC822': b'From: test@example.com\r\nSubject: Test Subject\r\n\r\nTest Body',
            b'SEQ': 1,
            b'UID': 12345,
            b'INTERNALDATE': datetime(2023, 3, 17, 12, 0, 0, tzinfo=timezone.utc),
        }
    }
    imap.__enter__.return_value = imap
    imap.__exit__.return_value = None
    return imap

@pytest.fixture
def test_env():
    """Returns test environment variables."""
    return {
        "EMAIL_ACCOUNT": "test@example.com",
        "GOOGLE_CLIENT_ID": "test-client-id",
        "GOOGLE_CLIENT_SECRET": "test-client-secret",
    }

@pytest.fixture
def mock_db():
    """Creates a mock DB with useful defaults for email operations.
    
    NOTE: There are issues with cursor mocking for MongoDB async operations.
    Current mocking approach is failing with: 'coroutine' object has no attribute 'sort'
    
    To properly fix this, we need to ensure that:
    1. AsyncMock is used for all database methods
    2. Returned values from find() should be properly configured with async chain methods
    3. Each method in the chain (.sort(), .skip(), .limit()) should return a properly configured AsyncMock
    4. Final cursor should have to_list as an AsyncMock that returns test data
    
    Currently some tests are disabled with @pytest.mark.skip while we resolve the proper mocking approach.
    """
    db_mock = MagicMock()
    
    # Setup mock cursor for find operations
    mock_cursor = AsyncMock()
    mock_emails = [{"email_id": "1", "sender": "test@example.com", "subject": "Test Subject"}]
    mock_cursor.to_list = AsyncMock(return_value=mock_emails)
    
    # Setup mock sort, skip and limit
    mock_sort = AsyncMock()
    mock_sort.skip = AsyncMock(return_value=mock_sort)
    mock_sort.limit = AsyncMock(return_value=mock_cursor)
    
    # Setup mock find
    mock_find = AsyncMock()
    mock_find.sort = AsyncMock(return_value=mock_sort)
    db_mock.emails.find = AsyncMock(return_value=mock_find)
    
    # Setup count
    db_mock.emails.count_documents = AsyncMock(return_value=1)
    
    # Setup find_one
    db_mock.emails.find_one = AsyncMock(return_value={"email_id": "12345", "subject": "Test Subject"})
    
    # Setup insert_one
    db_mock.emails.insert_one = AsyncMock()
    
    # Setup update_one
    update_result = MagicMock()
    update_result.matched_count = 1
    db_mock.emails.update_one = AsyncMock(return_value=update_result)
    
    # Setup delete_one
    delete_result = MagicMock()
    delete_result.deleted_count = 1
    db_mock.emails.delete_one = AsyncMock(return_value=delete_result)
    
    return db_mock 