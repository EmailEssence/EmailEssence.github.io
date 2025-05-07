"""
Unit tests for TokenRepository.
"""
import pytest
from app.services.database import TokenRepository
from app.models.auth_models import TokenData
from app.tests.database_mock import mock_token_collection, mock_token_repository
from app.tests.constants import mock_token_data

@pytest.mark.asyncio
async def test_find_by_google_id(mock_token_repository, mock_token_data):
    """Test retrieving a token by Google ID."""
    # Arrange
    google_id = "user123"
    
    # Act
    result = await mock_token_repository.find_by_google_id(google_id)
    
    # Assert
    assert result is not None
    assert isinstance(result, TokenData)
    assert result.google_id == google_id

@pytest.mark.asyncio
async def test_find_by_google_id_not_found(mock_token_repository):
    """Test retrieving a non-existent token by Google ID."""
    # Arrange
    google_id = "non_existent_user"
    
    # Act
    result = await mock_token_repository.find_by_google_id(google_id)
    
    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_update_by_google_id(mock_token_repository):
    """Test updating an existing token."""
    # Arrange
    google_id = "user123"
    update_data = {"token": "access_token_123"}
    
    # Act
    result = await mock_token_repository.update_by_google_id(google_id, update_data)
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_update_by_google_id_not_found(mock_token_repository):
    """Test updating a non-existent token."""
    # Arrange
    google_id = "non_existent_user"
    update_data = {"token": "new_test_token"}
    
    # Act
    result = await mock_token_repository.update_by_google_id(google_id, update_data)
    
    # Assert
    assert result is False

@pytest.mark.asyncio
async def test_delete_by_google_id(mock_token_repository):
    """Test deleting a token by Google ID."""
    # Arrange
    google_id = "user123"
    
    # Act
    result = await mock_token_repository.delete_by_google_id(google_id)
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_delete_by_google_id_not_found(mock_token_repository):
    """Test deleting a non-existent token by Google ID."""
    # Arrange
    google_id = "non_existent_user"
    
    # Act
    result = await mock_token_repository.delete_by_google_id(google_id)
    
    # Assert
    assert result is False 