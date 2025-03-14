import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi import HTTPException

import os
from datetime import datetime, timezone

from app.services.email_service import (
    get_auth_token,
    fetch_from_imap,
    fetch_emails
)

# Test get_auth_token
@pytest.mark.asyncio
async def test_get_auth_token_success():
    """Test successful token retrieval"""
    with patch('app.services.auth_service.get_credentials') as mock_get_credentials:
        # Create a mock credentials object
        mock_credentials = MagicMock()
        mock_credentials.valid = True
        mock_credentials.token = "test_token"
        mock_get_credentials.return_value = mock_credentials
        
        token = await get_auth_token()
        assert token == "test_token"

@pytest.mark.asyncio
async def test_get_auth_token_failure():
    """Test failed token retrieval"""
    with patch('app.services.auth_service.get_credentials') as mock_get_credentials:
        mock_get_credentials.side_effect = Exception("Auth failed")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_auth_token()
        assert exc_info.value.status_code == 401
        assert "Token retrieval failed" in str(exc_info.value.detail)

# TODO: Fix MongoDB cursor mocking - cursor.sort() is not properly mocked
@pytest.mark.skip(reason="MongoDB cursor mocking not working properly - cursor.sort() issue")
@pytest.mark.db
@pytest.mark.asyncio
async def test_fetch_emails_from_mongodb(mock_db, mock_threadpool, mock_imap_client):
    """Test fetching emails from MongoDB without IMAP refresh"""
    # Setup mock cursor and count
    mock_cursor = AsyncMock()
    mock_emails = [{"email_id": "1", "sender": "test@example.com", "subject": "Test Subject"}]
    mock_cursor.to_list = AsyncMock(return_value=mock_emails)
    mock_db.emails.find.return_value = mock_cursor
    mock_db.emails.count_documents = AsyncMock(return_value=1)
    
    # Patch the db object
    with patch('app.services.email_service.db', mock_db):
        # Call the function
        emails, total, debug_info = await fetch_emails()
        
        # Verify the result
        assert len(emails) == 1
        assert emails[0]["email_id"] == "1"
        assert emails[0]["sender"] == "test@example.com"
        assert emails[0]["subject"] == "Test Subject"
        assert total == 1
        assert "db_query" in debug_info
        assert "timing" in debug_info
        assert debug_info["source"] == "database"
        
        # Verify the find method was called with correct parameters
        mock_db.emails.find.assert_called_once()
        mock_db.emails.count_documents.assert_called_once()

# TODO: Fix MongoDB cursor mocking - cursor.sort() is not properly mocked
@pytest.mark.skip(reason="MongoDB cursor mocking not working properly - cursor.sort() issue")
@pytest.mark.db
@pytest.mark.asyncio
async def test_fetch_emails_no_email_account(mock_db, mock_threadpool):
    """Test error handling when EMAIL_ACCOUNT is not set"""
    # Create mock DB that returns empty list
    empty_cursor = AsyncMock()
    empty_cursor.to_list = AsyncMock(return_value=[])
    mock_db.emails.find.return_value = empty_cursor
    mock_db.emails.count_documents = AsyncMock(return_value=0)
    
    # Patch the DB, environment, and auth token
    with patch('app.services.email_service.db', mock_db):
        with patch.dict(os.environ, {}, clear=True):
            with patch('app.services.email_service.get_auth_token', return_value="test_token"):
                # Call with refresh=True to trigger IMAP fetch
                with pytest.raises(HTTPException) as exc_info:
                    await fetch_emails(refresh=True)
                assert exc_info.value.status_code == 500
                assert "EMAIL_ACCOUNT environment variable not set" in str(exc_info.value.detail)

# TODO: Fix MongoDB cursor mocking - cursor.sort() is not properly mocked
@pytest.mark.skip(reason="MongoDB cursor mocking not working properly - cursor.sort() issue")
@pytest.mark.db
@pytest.mark.asyncio
async def test_fetch_from_imap_success(mock_db, mock_threadpool, mock_imap_client):
    """Test successful IMAP fetch and DB update"""
    # Setup environment variables
    test_env = {
        "EMAIL_ACCOUNT": "test@example.com"
    }
    
    # Setup mock cursor and count
    mock_cursor = AsyncMock()
    mock_emails = [{"email_id": "1", "sender": "test@example.com", "subject": "Test Subject"}]
    mock_cursor.to_list = AsyncMock(return_value=mock_emails)
    mock_db.emails.find.return_value = mock_cursor
    mock_db.emails.count_documents = AsyncMock(return_value=1)
    
    # Setup mock IMAP response
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
    mock_threadpool.return_value = [test_email]
    
    # Patch necessary dependencies
    with patch.dict(os.environ, test_env):
        with patch('app.services.email_service.IMAPClient', return_value=mock_imap_client):
            with patch('app.services.email_service.run_in_threadpool', mock_threadpool):
                with patch('app.services.email_service.get_auth_token', return_value="test_token"):
                    with patch('app.services.email_service.db', mock_db):
                        with patch('app.services.email_service.save_email_to_db', new_callable=AsyncMock):
                            # Call the function with refresh=True to trigger IMAP fetch
                            emails, total, debug_info = await fetch_emails(refresh=True)
                            
                            # Verify results
                            assert len(emails) == 1
                            assert emails[0]["email_id"] == "1"
                            assert total == 1
                            assert debug_info["source"] == "imap+database"
                            assert "imap_fetch_count" in debug_info
                            
                            # Verify mock interactions
                            mock_imap_client.select_folder.assert_called_once_with('INBOX')
                            mock_imap_client.search.assert_called_once()
                            mock_imap_client.fetch.assert_called_once()

@pytest.mark.asyncio
@pytest.mark.skip(reason="MongoDB mocking not working properly")
async def test_fetch_from_imap_error(mock_imap_client):
    """Test error handling during IMAP fetch"""
    # Setup mock to raise an exception
    mock_imap_client.oauth2_login.side_effect = Exception("IMAP error")
    
    # Setup environment variables
    test_env = {
        "EMAIL_ACCOUNT": "test@example.com"
    }
    
    # Set up the threadpool mock to directly call the function
    async def mock_threadpool(func, *args, **kwargs):
        return func(*args, **kwargs)
    
    # Setup mock DB
    mock_db = AsyncMock()
    mock_cursor = AsyncMock()
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    
    # Make find() return the cursor directly, not a coroutine
    mock_db.emails.find.return_value = mock_cursor
    mock_db.emails.count_documents = AsyncMock(return_value=0)
    
    # Patch necessary dependencies
    with patch.dict(os.environ, test_env):
        with patch('app.services.email_service.IMAPClient', return_value=mock_imap_client):
            with patch('app.services.email_service.run_in_threadpool', mock_threadpool):
                with patch('app.services.email_service.get_auth_token', return_value="test_token"):
                    with patch('app.services.email_service.db', mock_db):
                        # The function should still return empty results from DB even if IMAP fails
                        emails, total, debug_info = await fetch_emails(refresh=True)
                        
                        # Verify results
                        assert len(emails) == 0
                        assert total == 0
                        assert "imap_error" in debug_info

# TODO: Fix MongoDB cursor mocking - cursor.sort() is not properly mocked
@pytest.mark.skip(reason="MongoDB cursor mocking not working properly - cursor.sort() issue")
@pytest.mark.db
@pytest.mark.asyncio
async def test_fetch_emails_with_filters(mock_db, mock_threadpool, mock_imap_client):
    """Test fetching emails with various filters"""
    # Setup mock cursor and count
    mock_cursor = AsyncMock()
    mock_emails = [{"email_id": "1", "sender": "test@example.com", "subject": "Test Subject"}]
    mock_cursor.to_list = AsyncMock(return_value=mock_emails)
    mock_db.emails.find.return_value = mock_cursor
    mock_db.emails.count_documents = AsyncMock(return_value=1)
    
    # Patch the db object
    with patch('app.services.email_service.db', mock_db):
        # Call the function with filters
        emails, total, debug_info = await fetch_emails(
            unread_only=True,
            category="important",
            search="test",
            sort_by="subject",
            sort_order="asc"
        )
        
        # Verify the result
        assert len(emails) == 1
        assert total == 1
        
        # Verify the query contained our filters
        find_call_args = mock_db.emails.find.call_args[0][0]
        assert find_call_args["is_read"] is False
        assert find_call_args["category"] == "important"
        assert "$or" in find_call_args
        
        # Verify sort was called correctly
        sort_call = mock_cursor.sort.call_args
        assert sort_call[0][0] == "subject"
        assert sort_call[0][1] == 1  # asc = 1