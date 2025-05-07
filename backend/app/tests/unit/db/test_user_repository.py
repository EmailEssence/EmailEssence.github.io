"""
Unit tests for UserRepository.
"""
import pytest
from app.services.database import UserRepository
from app.models.user_models import UserSchema, PreferencesSchema
from app.tests.database_mock import mock_user_collection, mock_user_repository
from app.tests.constants import mock_user

@pytest.mark.asyncio
async def test_create_user(mock_user_repository, mock_user):
    """Test creating a new user."""
    # Arrange
    user = mock_user
    
    # Act
    result = await mock_user_repository.insert_one(user)
    
    # Assert
    assert result is not None
    assert isinstance(result, str)  # Should return the ID
    assert result == "mock_id"  # From mock collection

@pytest.mark.asyncio
async def test_find_by_google_id(mock_user_repository, mock_user):
    """Test retrieving a user by Google ID."""
    # Arrange
    google_id = "user123"
    
    # Act
    result = await mock_user_repository.find_by_google_id(google_id)
    
    # Assert
    assert result is not None
    assert isinstance(result, UserSchema)
    assert result.google_id == google_id

@pytest.mark.asyncio
async def test_find_by_google_id_not_found(mock_user_repository):
    """Test retrieving a non-existent user by Google ID."""
    # Arrange
    google_id = "non_existent_user"
    
    # Act
    result = await mock_user_repository.find_by_google_id(google_id)
    
    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_find_by_email(mock_user_repository, mock_user):
    """Test retrieving a user by email."""
    # Arrange
    email = "user@example.com"
    
    # Act
    result = await mock_user_repository.find_by_email(email)
    
    # Assert
    assert result is not None
    assert isinstance(result, UserSchema)
    assert result.email == email

@pytest.mark.asyncio
async def test_find_by_email_not_found(mock_user_repository):
    """Test retrieving a non-existent user by email."""
    # Arrange
    email = "non_existent@test.com"
    
    # Act
    result = await mock_user_repository.find_by_email(email)
    
    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_update_preferences(mock_user_repository, mock_user):
    """Test updating user preferences."""
    # Arrange
    google_id = "user123"
    new_preferences = PreferencesSchema(
        summaries=True,
        theme="dark",
        fetch_frequency="60"
    )
    
    # Act
    result = await mock_user_repository.update_preferences(google_id, new_preferences.model_dump())
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_update_preferences_not_found(mock_user_repository):
    """Test updating preferences for a non-existent user."""
    # Arrange
    google_id = "non_existent_user"
    new_preferences = PreferencesSchema(
        summaries=True,
        theme="dark",
        fetch_frequency="60"
    )
    
    # Act
    result = await mock_user_repository.update_preferences(google_id, new_preferences.model_dump())
    
    # Assert
    assert result is False

@pytest.mark.asyncio
async def test_delete_by_google_id(mock_user_repository):
    """Test deleting a user by Google ID."""
    # Arrange
    google_id = "user123"
    
    # Act
    result = await mock_user_repository.delete_by_google_id(google_id)
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_delete_by_google_id_not_found(mock_user_repository):
    """Test deleting a non-existent user by Google ID."""
    # Arrange
    google_id = "non_existent_user"
    
    # Act
    result = await mock_user_repository.delete_by_google_id(google_id)
    
    # Assert
    assert result is False 