"""
Tests for the EmailService class.

This module contains high-level tests for the EmailService class and its
central functionality, focusing on the core service methods.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
from fastapi import HTTPException

from app.services import EmailService

# =============================================================================
# Authentication Method Tests
# =============================================================================

@pytest.mark.asyncio
async def test_get_auth_token_success(email_service, mock_credentials):
    """Test successfully getting an auth token."""
    with patch('app.services.auth_service.get_credentials', return_value=mock_credentials):
        with patch('app.services.email_service.run_in_threadpool', new_callable=AsyncMock) as mock_threadpool:
            mock_threadpool.side_effect = lambda x: x() if callable(x) else x
            
            token = await email_service.get_auth_token()
            
            assert token == "test_token"
            assert mock_threadpool.called

@pytest.mark.asyncio
async def test_get_auth_token_expired_refreshable(email_service, mock_credentials):
    """Test getting an auth token with expired but refreshable credentials."""
    mock_credentials.valid = False
    mock_credentials.expired = True
    
    with patch('app.services.auth_service.get_credentials', return_value=mock_credentials):
        with patch('app.services.email_service.run_in_threadpool', new_callable=AsyncMock) as mock_threadpool:
            mock_threadpool.side_effect = lambda x: x() if callable(x) else x
            
            token = await email_service.get_auth_token()
            
            assert token == "test_token"
            assert mock_credentials.refresh.called

@pytest.mark.asyncio
async def test_get_auth_token_expired_not_refreshable(email_service, mock_credentials):
    """Test getting an auth token with expired and non-refreshable credentials."""
    mock_credentials.valid = False
    mock_credentials.expired = True
    mock_credentials.refresh_token = None
    
    with patch('app.services.auth_service.get_credentials', return_value=mock_credentials):
        with patch('app.services.email_service.run_in_threadpool', new_callable=AsyncMock) as mock_threadpool:
            mock_threadpool.side_effect = lambda x: x() if callable(x) else x
            
            with pytest.raises(HTTPException) as exc_info:
                await email_service.get_auth_token()
            
            assert exc_info.value.status_code == 401
            assert "Token expired and cannot be refreshed" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_auth_token_exception(email_service):
    """Test getting an auth token with an exception."""
    with patch('app.services.auth_service.get_credentials', side_effect=Exception("Auth failed")):
        with patch('app.services.email_service.run_in_threadpool', new_callable=AsyncMock) as mock_threadpool:
            # Make run_in_threadpool raise the exception when received
            mock_threadpool.side_effect = lambda x: raise_(x) if isinstance(x, Exception) else x()
            
            with pytest.raises(HTTPException) as exc_info:
                await email_service.get_auth_token()
            
            assert exc_info.value.status_code == 401
            assert "Token retrieval failed" in str(exc_info.value.detail)

# Helper function to raise exceptions in lambda
def raise_(ex):
    raise ex

# =============================================================================
# Content Processing Tests
# =============================================================================

@pytest.mark.asyncio
async def test_get_email_reader_view(email_service, mock_db):
    """Test generating a reader view for an email."""
    # Mock email data
    mock_email = {
        "email_id": "12345",
        "subject": "Test Subject",
        "sender": "test@example.com",
        "body": "<div>This is an HTML email</div>",
        "is_read": False,
        "received_at": datetime.now(timezone.utc)
    }
    
    with patch('app.services.email_service.db', mock_db):
        # Override the default find_one response
        mock_db.emails.find_one = AsyncMock(return_value=mock_email)
        
        # Mock the EmailSchema and ReaderViewResponse
        with patch('app.models.EmailSchema') as mock_email_schema:
            with patch('app.models.ReaderViewResponse') as mock_reader_view_response:
                # Setup EmailSchema instance
                mock_email_obj = MagicMock()
                mock_email_obj.body = mock_email["body"]
                mock_email_schema.return_value = mock_email_obj
                
                # Setup ReaderViewResponse.from_email
                mock_reader_view = MagicMock()
                mock_reader_view_response.from_email.return_value = mock_reader_view
                
                # Call the function
                result = await email_service.get_email_reader_view("12345")
                
                # Verify results
                assert result == mock_reader_view
                mock_db.emails.find_one.assert_called_once_with({"email_id": "12345"})
                mock_email_schema.assert_called_once()
                mock_reader_view_response.from_email.assert_called_once()

@pytest.mark.asyncio
async def test_get_email_reader_view_not_found(email_service, mock_db):
    """Test generating a reader view for a non-existent email."""
    with patch('app.services.email_service.db', mock_db):
        # Override the default find_one response
        mock_db.emails.find_one = AsyncMock(return_value=None)
        
        # Call the function
        result = await email_service.get_email_reader_view("12345")
        
        # Verify results
        assert result is None
        mock_db.emails.find_one.assert_called_once_with({"email_id": "12345"})

# =============================================================================
# Public API Method Tests
# =============================================================================

@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
@pytest.mark.asyncio
async def test_fetch_emails(email_service, mock_db):
    """Test the main fetch_emails function."""
    with patch('app.services.email_service.db', mock_db):
        # Call the function
        emails, total, debug_info = await email_service.fetch_emails()
        
        # Verify results
        assert len(emails) == 1
        assert emails[0]["email_id"] == "1"
        assert total == 1
        assert debug_info["source"] == "database"
        
        # Verify method calls
        mock_db.emails.find.assert_called_once()
        mock_db.emails.count_documents.assert_called_once()

@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
@pytest.mark.asyncio
async def test_fetch_emails_with_refresh(email_service, mock_db):
    """Test fetch_emails with refresh=True."""
    with patch('app.services.email_service.db', mock_db):
        with patch.object(email_service, '_refresh_emails_from_imap') as mock_refresh:
            # Call with refresh=True
            emails, total, debug_info = await email_service.fetch_emails(refresh=True)
            
            # Verify results
            assert len(emails) == 1
            assert emails[0]["email_id"] == "1"
            assert total == 1
            
            # _refresh_emails_from_imap should be called
            mock_refresh.assert_called_once()

@pytest.mark.asyncio
async def test_refresh_emails_from_imap(email_service, mock_db):
    """Test the internal _refresh_emails_from_imap method."""
    debug_info = {"source": "database", "timing": {}}
    
    with patch('app.services.email_service.db', mock_db):
        with patch.object(email_service, 'get_auth_token', return_value="test_token"):
            with patch.object(email_service, 'fetch_from_imap') as mock_fetch:
                mock_fetch.return_value = [
                    {"email_id": "12345", "subject": "Fetched Email"}
                ]
                
                # Call the method
                await email_service._refresh_emails_from_imap(debug_info)
                
                # Verify results
                assert debug_info["source"] == "imap+database"
                assert "imap_fetch_count" in debug_info
                assert debug_info["imap_fetch_count"] == 1
                
                # Verify method calls
                mock_fetch.assert_called_once()

def test_build_email_query(email_service):
    """Test building the email query filter."""
    # Test with default parameters
    query = email_service._build_email_query(False, None, None)
    assert query == {}
    
    # Test with unread_only
    query = email_service._build_email_query(True, None, None)
    assert query == {"is_read": False}
    
    # Test with category
    query = email_service._build_email_query(False, "inbox", None)
    assert query == {"category": "inbox"}
    
    # Test with search
    query = email_service._build_email_query(False, None, "test")
    assert "$or" in query
    assert len(query["$or"]) == 3  # subject, body, sender
    
    # Test with all parameters
    query = email_service._build_email_query(True, "inbox", "test")
    assert query["is_read"] is False
    assert query["category"] == "inbox"
    assert "$or" in query 