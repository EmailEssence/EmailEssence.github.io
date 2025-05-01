"""
Tests for the BaseRepository class.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId

from app.models.email_models import EmailSchema


@pytest.mark.asyncio
async def test_find_one(mock_email_repository):
    """Test find_one method."""
    # Find by email_id
    email = await mock_email_repository.find_one({"email_id": "test_1"})
    assert email is not None
    assert email.email_id == "test_1"
    assert email.subject == "Test Email 1"
    
    # Find by a non-existent ID
    email = await mock_email_repository.find_one({"email_id": "non_existent"})
    assert email is None


@pytest.mark.asyncio
async def test_find_by_id(mock_email_repository):
    """Test find_by_id method."""
    # Create a valid ObjectId for testing
    valid_object_id = "507f1f77bcf86cd799439011"  # 24-char hex string (12 bytes)
    
    # Mock the find_one method to return a document for a specific ID
    mock_email_repository.find_one = AsyncMock(return_value=EmailSchema(
        email_id="test_id", 
        google_id="user123",
        sender="test@example.com",
        recipients=["user@example.com"],
        subject="Test Subject",
        body="Test Body"
    ))
    
    # Test the method
    email = await mock_email_repository.find_by_id(valid_object_id)
    assert email is not None
    assert email.email_id == "test_id"


@pytest.mark.asyncio
async def test_find_many(mock_email_repository):
    """Test find_many method."""
    emails = await mock_email_repository.find_many({"google_id": "user123"})
    assert len(emails) == 2
    assert emails[0].email_id == "test_1"
    assert emails[1].email_id == "test_2"


@pytest.mark.asyncio
async def test_insert_one(mock_email_repository):
    """Test insert_one method."""
    new_email = EmailSchema(
        email_id="test_3", 
        google_id="user123",
        sender="new@example.com",
        recipients=["recipient@example.com"],
        subject="New Test Email",
        body="This is a new test email body"
    )
    
    result = await mock_email_repository.insert_one(new_email)
    assert result == "mock_id"
    mock_email_repository.collection.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_update_one(mock_email_repository):
    """Test update_one method."""
    update_data = {"is_read": True}
    result = await mock_email_repository.update_one({"email_id": "test_1"}, update_data)
    assert result is True
    mock_email_repository.collection.update_one.assert_called_once_with(
        {"email_id": "test_1"}, {"$set": update_data}, upsert=False
    )


@pytest.mark.asyncio
async def test_delete_one(mock_email_repository):
    """Test delete_one method."""
    result = await mock_email_repository.delete_one({"email_id": "test_1"})
    assert result is True
    mock_email_repository.collection.delete_one.assert_called_once_with({"email_id": "test_1"})


@pytest.mark.asyncio
async def test_count_documents(mock_email_repository):
    """Test count_documents method."""
    count = await mock_email_repository.count_documents({"is_read": False})
    assert count == 2  # This will use the default mock setting
