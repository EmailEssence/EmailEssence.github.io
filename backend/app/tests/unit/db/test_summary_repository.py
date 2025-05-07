"""
Unit tests for SummaryRepository.
"""
import pytest
from datetime import datetime, timezone
from app.services.database import SummaryRepository
from app.models.summary_models import SummarySchema
from app.tests.database_mock import mock_summary_collection, mock_summary_repository
from app.tests.constants import mock_summary_schema

@pytest.mark.asyncio
async def test_find_by_email_id(mock_summary_repository, mock_summary_schema):
    """Test retrieving a summary by email ID."""
    # Arrange
    email_id = "test_1"
    
    # Act
    result = await mock_summary_repository.find_by_email_id(email_id)
    
    # Assert
    assert result is not None
    assert isinstance(result, SummarySchema)
    assert result.email_id == email_id

@pytest.mark.asyncio
async def test_find_by_email_id_not_found(mock_summary_repository):
    """Test retrieving a non-existent summary by email ID."""
    # Arrange
    email_id = "non_existent_id"
    
    # Act
    result = await mock_summary_repository.find_by_email_id(email_id)
    
    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_find_by_google_id(mock_summary_repository, mock_summary_schema):
    """Test retrieving summaries by Google ID."""
    # Arrange
    google_id = "user123"
    
    # Act
    result = await mock_summary_repository.find_by_google_id(google_id)
    
    # Assert
    assert result is not None
    assert len(result) > 0
    assert all(isinstance(summary, SummarySchema) for summary in result)
    assert all(summary.google_id == google_id for summary in result)

@pytest.mark.asyncio
async def test_find_by_google_id_not_found(mock_summary_repository):
    """Test retrieving summaries for a non-existent Google ID."""
    # Arrange
    google_id = "non_existent_user"
    
    # Act
    result = await mock_summary_repository.find_by_google_id(google_id)
    
    # Assert
    assert result is not None
    assert len(result) == 0

@pytest.mark.asyncio
async def test_update_by_email_id(mock_summary_repository):
    """Test updating a summary by email ID."""
    # Arrange
    email_id = "test_1"
    update_data = {"summary_text": "Updated summary"}
    
    # Act
    result = await mock_summary_repository.update_by_email_id(email_id, update_data)
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_update_by_email_id_not_found(mock_summary_repository):
    """Test updating a non-existent summary by email ID."""
    # Arrange
    email_id = "non_existent_id"
    update_data = {"summary_text": "Updated summary"}
    
    # Act
    result = await mock_summary_repository.update_by_email_id(email_id, update_data)
    
    # Assert
    assert result is False

@pytest.mark.asyncio
async def test_delete_by_email_and_google_id(mock_summary_repository):
    """Test deleting a summary by email ID and Google ID."""
    # Arrange
    email_id = "test_1"
    google_id = "user123"
    
    # Act
    result = await mock_summary_repository.delete_by_email_and_google_id(email_id, google_id)
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_delete_by_email_and_google_id_not_found(mock_summary_repository):
    """Test deleting a non-existent summary by email ID and Google ID."""
    # Arrange
    email_id = "non_existent_id"
    google_id = "non_existent_user"
    
    # Act
    result = await mock_summary_repository.delete_by_email_and_google_id(email_id, google_id)
    
    # Assert
    assert result is False 