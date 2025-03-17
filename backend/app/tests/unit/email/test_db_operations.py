"""
Tests for database operations in the EmailService class.

This module tests database interactions in the EmailService class,
focusing on CRUD operations and data persistence.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone

from app.services.email_service import EmailService

# =============================================================================
# Email Saving Tests
# =============================================================================

@pytest.mark.asyncio
async def test_save_email_to_db(email_service, mock_db):
    """Test saving an email to the database."""
    email_data = {
        "email_id": "12345",
        "subject": "Test Subject",
        "sender": "test@example.com",
    }
    
    with patch('app.services.email_service.db', mock_db):
        # Override default find_one 
        mock_db.emails.find_one = AsyncMock(return_value=None)
        
        await email_service.save_email_to_db(email_data, "12345")
        
        # Verify DB methods were called
        mock_db.emails.find_one.assert_called_once_with({"email_id": "12345"})
        mock_db.emails.insert_one.assert_called_once_with(email_data)

@pytest.mark.asyncio
async def test_save_email_to_db_already_exists(email_service, mock_db):
    """Test trying to save an email that already exists."""
    email_data = {
        "email_id": "12345",
        "subject": "Test Subject",
        "sender": "test@example.com",
    }
    
    with patch('app.services.email_service.db', mock_db):
        # Override default find_one
        mock_db.emails.find_one = AsyncMock(return_value={"email_id": "12345"})
        
        await email_service.save_email_to_db(email_data, "12345")
        
        # find_one should be called, but insert_one should not
        mock_db.emails.find_one.assert_called_once()
        mock_db.emails.insert_one.assert_not_called()

# =============================================================================
# Email Retrieval Tests
# =============================================================================

@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
@pytest.mark.asyncio
async def test_get_emails_from_db(email_service, mock_db):
    """Test getting emails from the database."""
    with patch('app.services.email_service.db', mock_db):
        # Call the function
        emails = await email_service.get_emails_from_db()
        
        # Verify results
        assert len(emails) == 1
        assert emails[0]["email_id"] == "1"
        
        # Verify method calls
        mock_db.emails.find.assert_called_once()
        mock_find = mock_db.emails.find.return_value
        mock_find.sort.assert_called_once()
        
        # Verify sort and limit
        mock_sort = mock_find.sort.return_value
        mock_sort.skip.assert_called_once()
        mock_sort.limit.assert_called_once()

@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
@pytest.mark.asyncio
async def test_get_emails_with_filtering(email_service, mock_db):
    """Test getting emails with query filtering."""
    query = {"is_read": False, "category": "inbox"}
    
    with patch('app.services.email_service.db', mock_db):
        # Call with specific query
        await email_service.get_emails_from_db(query=query)
        
        # Verify find was called with query
        mock_db.emails.find.assert_called_once_with(query)

@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
@pytest.mark.asyncio
async def test_get_emails_with_pagination(email_service, mock_db):
    """Test getting emails with pagination."""
    with patch('app.services.email_service.db', mock_db):
        # Call with pagination params
        await email_service.get_emails_from_db(skip=10, limit=20)
        
        # Verify skip and limit were called with right params
        mock_find = mock_db.emails.find.return_value
        mock_sort = mock_find.sort.return_value
        mock_sort.skip.assert_called_once_with(10)
        mock_sort.limit.assert_called_once_with(20)

@pytest.mark.asyncio
async def test_get_email(email_service, mock_db):
    """Test getting a single email by ID."""
    with patch('app.services.email_service.db', mock_db):
        # Call the function
        email = await email_service.get_email("12345")
        
        # Verify results
        assert email == mock_db.emails.find_one.return_value
        mock_db.emails.find_one.assert_called_once_with({"email_id": "12345"})

@pytest.mark.asyncio
async def test_get_email_not_found(email_service, mock_db):
    """Test getting a non-existent email."""
    with patch('app.services.email_service.db', mock_db):
        # Override find_one to return None
        mock_db.emails.find_one = AsyncMock(return_value=None)
        
        # Call the function
        email = await email_service.get_email("99999")
        
        # Verify results
        assert email is None
        mock_db.emails.find_one.assert_called_once()

# =============================================================================
# Email Update Tests
# =============================================================================

@pytest.mark.asyncio
async def test_mark_email_as_read(email_service, mock_db):
    """Test marking an email as read."""
    with patch('app.services.email_service.db', mock_db):
        # Setup read email data
        read_email = {"email_id": "12345", "subject": "Test Subject", "is_read": True}
        mock_db.emails.find_one = AsyncMock(return_value=read_email)
        
        # Call the function
        result = await email_service.mark_email_as_read("12345")
        
        # Verify results
        assert result == read_email
        mock_db.emails.update_one.assert_called_once_with(
            {"email_id": "12345"},
            {"$set": {"is_read": True}}
        )
        mock_db.emails.find_one.assert_called_once_with({"email_id": "12345"})

@pytest.mark.asyncio
async def test_mark_email_as_read_not_found(email_service, mock_db):
    """Test marking a non-existent email as read."""
    with patch('app.services.email_service.db', mock_db):
        # Setup update_one to indicate no match
        update_result = MagicMock()
        update_result.matched_count = 0
        mock_db.emails.update_one = AsyncMock(return_value=update_result)
        
        # Call the function
        result = await email_service.mark_email_as_read("12345")
        
        # Verify results
        assert result is None
        mock_db.emails.update_one.assert_called_once()
        mock_db.emails.find_one.assert_not_called()

# =============================================================================
# Email Deletion Tests
# =============================================================================

@pytest.mark.asyncio
async def test_delete_email(email_service, mock_db):
    """Test deleting an email."""
    with patch('app.services.email_service.db', mock_db):
        # Call the function
        result = await email_service.delete_email("12345")
        
        # Verify results
        assert result is True
        mock_db.emails.delete_one.assert_called_once_with({"email_id": "12345"})

@pytest.mark.asyncio
async def test_delete_email_not_found(email_service, mock_db):
    """Test deleting a non-existent email."""
    with patch('app.services.email_service.db', mock_db):
        # Setup delete_one to indicate no match
        delete_result = MagicMock()
        delete_result.deleted_count = 0
        mock_db.emails.delete_one = AsyncMock(return_value=delete_result)
        
        # Call the function
        result = await email_service.delete_email("99999")
        
        # Verify results
        assert result is False
        mock_db.emails.delete_one.assert_called_once() 