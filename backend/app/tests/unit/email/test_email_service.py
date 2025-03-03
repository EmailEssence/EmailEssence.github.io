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

# Test fetch_emails
@pytest.mark.skip(reason="Database implementation issues - to be fixed later")
@pytest.mark.asyncio
async def test_fetch_emails_from_mongodb(mock_db):
    """Test fetching emails from MongoDB cache"""
    # Ensure the mock_db fixture is correctly set up with .return_value not direct assignment
    # This is already handled in the constants.py mock_db fixture
    
    # Patch the db object
    with patch('app.services.email_service.db', mock_db):
        # Call the function
        result = await fetch_emails()
        
        # Verify the result
        assert len(result) == 1
        assert result[0]["email_id"] == "1"
        assert result[0]["sender"] == "test@example.com"
        assert result[0]["subject"] == "Test Subject"
        # Verify the find method was called
        mock_db.emails.find.assert_called_once()


@pytest.mark.skip(reason="Database implementation issues - to be fixed later")
@pytest.mark.asyncio
async def test_fetch_emails_no_email_account(mock_db):
    """Test fetching emails with no email account configured"""
    # Create mock DB that returns empty list
    empty_cursor = AsyncMock()
    empty_cursor.to_list = AsyncMock(return_value=[])
    mock_db.emails.find.return_value = empty_cursor
    
    # Patch the DB, environment, and auth token
    with patch('app.services.email_service.db', mock_db):
        with patch.dict(os.environ, {}, clear=True):
            with patch('app.services.email_service.get_auth_token', return_value="test_token"):
                with pytest.raises(HTTPException) as exc_info:
                    await fetch_emails()
                assert exc_info.value.status_code == 500
                assert "Email account not configured" in str(exc_info.value.detail)

# Test fetch_from_imap
@pytest.mark.skip(reason="Database implementation issues - to be fixed later")
@pytest.mark.asyncio
async def test_fetch_from_imap_success(mock_imap_client, mock_credentials, mock_db, mock_threadpool):
    """Test successful email retrieval from IMAP server"""
    # Setup environment variables
    test_env = {
        "EMAIL_ACCOUNT": "test@example.com"
    }
    
    # Patch necessary dependencies
    with patch.dict(os.environ, test_env):
        with patch('app.services.email_service.IMAPClient', return_value=mock_imap_client):
            with patch('app.services.email_service.run_in_threadpool', mock_threadpool):
                with patch('app.services.email_service.get_auth_token', return_value="test_token"):
                    with patch('app.services.email_service.db', mock_db):
                        # Call the main fetch_emails function which calls fetch_from_imap
                        result = await fetch_emails()
                        
                        # Verify results match EmailSchema format
                        assert len(result) == 1
                        assert "email_id" in result[0]
                        assert "user_id" in result[0]
                        assert "sender" in result[0]
                        assert "recipients" in result[0]
                        assert "subject" in result[0]
                        assert "body" in result[0]
                        assert "received_at" in result[0]
                        assert "category" in result[0]
                        assert "is_read" in result[0]
                        
                        # Verify mock interactions
                        mock_imap_client.select_folder.assert_called_once_with('INBOX')
                        mock_imap_client.search.assert_called_once()
                        mock_imap_client.fetch.assert_called_once()

@pytest.mark.asyncio
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
    
    # Patch necessary dependencies
    with patch.dict(os.environ, test_env):
        with patch('app.services.email_service.IMAPClient', return_value=mock_imap_client):
            with patch('app.services.email_service.run_in_threadpool', mock_threadpool):
                with patch('app.services.email_service.get_auth_token', return_value="test_token"):
                    with pytest.raises(HTTPException) as exc_info:
                        await fetch_emails()
                    assert exc_info.value.status_code == 500
                    assert "Failed to fetch emails" in str(exc_info.value.detail)

@pytest.mark.skip(reason="Database implementation issues - to be fixed later")
@pytest.mark.asyncio
async def test_fetch_emails_empty_db_uses_imap(mock_imap_client, mock_empty_db_cursor, mock_threadpool):
    """Test that when MongoDB is empty, emails are fetched from IMAP"""
    # Setup a mock DB with the correct cursor mock
    mock_db = AsyncMock()
    mock_db.emails = AsyncMock()
    mock_db.emails.find.return_value = mock_empty_db_cursor
    
    # Setup environment variables
    test_env = {
        "EMAIL_ACCOUNT": "test@example.com"
    }
    
    # Prepare mock IMAP response
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
                            # Call the function
                            result = await fetch_emails()
                            
                            # Verify IMAP was used
                            assert len(result) == 1
                            assert result[0]["email_id"] == "1"
                            
                            # Verify interactions with dependencies
                            mock_imap_client.select_folder.assert_called_once()
                            mock_imap_client.search.assert_called_once()
                            mock_imap_client.fetch.assert_called_once()