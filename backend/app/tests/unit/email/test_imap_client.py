# Test fetch_from_imap
import os
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from app.services.email_service import fetch_emails, fetch_from_imap


def test_fetch_from_imap_success():
    """Test successful IMAP email fetching"""
    token = "test_token"
    email_account = "test@example.com"
    
    # Create a mock IMAP client
    mock_imap = MagicMock()
    mock_imap.search.return_value = [1]
    mock_imap.fetch.return_value = {
        1: {
            b'RFC822': b'From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test\r\n\r\nBody',
            b'INTERNALDATE': datetime.now()
        }
    }
    mock_imap.__enter__.return_value = mock_imap
    
    # Patch the IMAPClient constructor
    with patch('app.services.email_service.IMAPClient', return_value=mock_imap):
        emails = fetch_from_imap(token, email_account)
        
        assert len(emails) == 1
        assert emails[0]["email_id"] == "1"
        mock_imap.oauth2_login.assert_called_once_with(email_account, token)

def test_fetch_from_imap_auth_failure():
    """Test IMAP authentication failure"""
    # Create a mock IMAP client
    mock_imap = MagicMock()
    mock_imap.oauth2_login.side_effect = Exception("Auth failed")
    mock_imap.__enter__.return_value = mock_imap
    
    # Patch the IMAPClient constructor
    with patch('app.services.email_service.IMAPClient', return_value=mock_imap):
        with pytest.raises(Exception) as exc_info:
            fetch_from_imap("invalid_token", "test@example.com")
        assert "Auth failed" in str(exc_info.value)
    
@pytest.mark.skip(reason="Database implementation issues - to be fixed later")
@pytest.mark.db
@pytest.mark.asyncio
async def test_fetch_emails_from_imap(mock_db, mock_threadpool, mock_imap_client):
    """Test fetching emails from IMAP when MongoDB is empty"""
    # Create a proper empty DB cursor mock
    empty_cursor = AsyncMock()
    empty_cursor.to_list = AsyncMock(return_value=[])
    
    # Setup the mock DB to return the empty cursor
    mock_db.emails.find.return_value = empty_cursor
    
    # Mock environment and DB
    with patch.dict(os.environ, {'EMAIL_ACCOUNT': 'test@example.com'}):
        with patch('app.services.email_service.db', mock_db):
            # Mock auth token
            with patch('app.services.email_service.get_auth_token') as mock_get_token:
                mock_get_token.return_value = "test_token"
                
                # Setup mock IMAP response via threadpool
                test_email = {
                    "user_id": "default",
                    "email_id": "1",
                    "sender": "test@example.com",
                    "recipients": ["recipient@example.com"],
                    "subject": "Test Subject",
                    "body": "Test content",
                    "received_at": datetime.now(),
                    "category": "uncategorized",
                    "is_read": False
                }
                mock_threadpool.return_value = [test_email]
                
                # Mock IMAP client
                with patch('app.services.email_service.IMAPClient', return_value=mock_imap_client):
                    # Mock save_email_to_db to do nothing
                    with patch('app.services.email_service.save_email_to_db', new_callable=AsyncMock):
                        # Mock run_in_threadpool
                        with patch('app.services.email_service.run_in_threadpool', mock_threadpool):
                            result = await fetch_emails()
                            
                            assert len(result) == 1
                            assert result[0]["email_id"] == "1"
                            assert result[0]["sender"] == "test@example.com"
                            assert "user_id" in result[0]
                            assert "recipients" in result[0]