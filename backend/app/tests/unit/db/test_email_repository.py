"""
Tests for the EmailRepository class.
"""
import pytest
from unittest.mock import AsyncMock

from app.models.email_models import EmailSchema

@pytest.mark.asyncio
async def test_find_by_email_id(mock_email_repository):
    """Test find_by_email_id method."""
    email = await mock_email_repository.find_by_email_id("test_1")
    assert email is not None
    assert email.email_id == "test_1"
    assert email.subject == "Test Email 1"
    
    mock_email_repository.collection.find_one.assert_called_with({"email_id": "test_1"})


@pytest.mark.asyncio
async def test_find_by_google_id(mock_email_repository):
    """Test find_by_google_id method."""
    emails = await mock_email_repository.find_by_google_id("user123")
    assert len(emails) == 2
    
    mock_email_repository.collection.find.assert_called_with({"google_id": "user123"})


@pytest.mark.asyncio
async def test_find_by_email_and_google_id(mock_email_repository):
    """Test find_by_email_and_google_id method."""
    # Setup the mock
    mock_email_repository.find_one = AsyncMock(return_value=EmailSchema(
        email_id="test_1", 
        google_id="user123",
        sender="test@example.com",
        recipients=["user@example.com"],
        subject="Test Subject",
        body="Test Body"
    ))
    
    email = await mock_email_repository.find_by_email_and_google_id("test_1", "user123")
    assert email is not None
    assert email.email_id == "test_1"
    
    mock_email_repository.find_one.assert_called_with({"email_id": "test_1", "google_id": "user123"})


@pytest.mark.asyncio
async def test_update_by_email_and_google_id(mock_email_repository):
    """Test update_by_email_and_google_id method."""
    # Setup the mock
    mock_email_repository.update_one = AsyncMock(return_value=True)
    
    update_data = {"is_read": True}
    result = await mock_email_repository.update_by_email_and_google_id("test_1", "user123", update_data)
    assert result is True
    
    mock_email_repository.update_one.assert_called_with(
        {"email_id": "test_1", "google_id": "user123"}, 
        update_data
    )


@pytest.mark.asyncio
async def test_delete_by_email_and_google_id(mock_email_repository):
    """Test delete_by_email_and_google_id method."""
    # Setup the mock
    mock_email_repository.delete_one = AsyncMock(return_value=True)
    
    result = await mock_email_repository.delete_by_email_and_google_id("test_1", "user123")
    assert result is True
    
    mock_email_repository.delete_one.assert_called_with({"email_id": "test_1", "google_id": "user123"})


@pytest.mark.asyncio
async def test_mark_as_read(mock_email_repository):
    """Test mark_as_read method."""
    # Setup mocks
    mock_email_repository.update_one = AsyncMock(return_value=True)
    mock_email_repository.find_by_email_id = AsyncMock(return_value=EmailSchema(
        email_id="test_1", 
        google_id="user123",
        sender="test@example.com",
        recipients=["user@example.com"],
        subject="Test Subject",
        body="Test Body",
        is_read=True
    ))
    
    email = await mock_email_repository.mark_as_read("test_1")
    assert email is not None
    assert email.is_read is True
    
    mock_email_repository.update_one.assert_called_with(
        {"email_id": "test_1"}, 
        {"$set": {"is_read": True}}
    )
    mock_email_repository.find_by_email_id.assert_called_with("test_1")
