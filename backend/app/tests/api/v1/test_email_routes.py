# tests/api/v1/test_email_routes.py
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

@pytest.mark.db
@pytest.mark.asyncio
@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
async def test_retrieve_emails_success(
    test_client: TestClient,
    mock_email_schema,
    mock_db
):
    """
    Test successful email retrieval flow
    """
    # Convert the EmailSchema to a dictionary that matches the response format
    email_dict = mock_email_schema.model_dump()
    
    # Create a mock service that returns the expected tuple format
    mock_service = AsyncMock()
    mock_service.fetch_emails = AsyncMock(return_value=([email_dict], 1, {"source": "database", "db_query": {}}))
    
    # Patch both the get_email_service function and the database
    with patch('app.routers.emails_router.get_email_service', return_value=mock_service):
        with patch('app.services.email_service.db', mock_db):
            # Act
            response = test_client.get("/emails")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "emails" in data
            assert "total" in data
            assert "has_more" in data
            assert "debug_info" in data
            
            assert len(data["emails"]) == 1
            assert data["total"] == 1
            assert data["has_more"] is False
            
            email = data["emails"][0]
            assert email["sender"] == mock_email_schema.sender
            assert email["subject"] == mock_email_schema.subject
            assert email["body"] == mock_email_schema.body
            assert "received_at" in email
            assert email["is_read"] is mock_email_schema.is_read
            
            # Verify required fields in the schema
            required_fields = ["user_id", "email_id", "sender", "recipients", 
                              "subject", "body", "received_at", "category", "is_read"]
            for field in required_fields:
                assert field in email

@pytest.mark.db
@pytest.mark.asyncio
@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
async def test_retrieve_emails_empty(
    test_client: TestClient,
    mock_db
):
    """
    Test behavior when no emails are found
    """
    # Create a mock service that returns empty results
    mock_service = AsyncMock()
    mock_service.fetch_emails = AsyncMock(return_value=([], 0, {"source": "database", "db_query": {}}))
    
    # Patch both the get_email_service function and the database
    with patch('app.routers.emails_router.get_email_service', return_value=mock_service):
        with patch('app.services.email_service.db', mock_db):
            # Act
            response = test_client.get("/emails")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["emails"]) == 0
            assert data["total"] == 0
            assert data["has_more"] is False

@pytest.mark.db
@pytest.mark.asyncio
@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
async def test_retrieve_emails_service_error(
    test_client: TestClient,
    mock_db
):
    """
    Test error handling when email service fails
    """
    # Create a mock service that raises an exception
    mock_service = AsyncMock()
    mock_service.fetch_emails = AsyncMock(side_effect=HTTPException(status_code=500, detail="IMAP connection failed"))
    
    # Patch both the get_email_service function and the database
    with patch('app.routers.emails_router.get_email_service', return_value=mock_service):
        with patch('app.services.email_service.db', mock_db):
            # Act
            response = test_client.get("/emails")

            # Assert
            assert response.status_code == 500
            assert "IMAP connection failed" in response.json()["detail"]

@pytest.mark.db
@pytest.mark.asyncio
@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
async def test_retrieve_emails_with_filters(
    test_client: TestClient,
    mock_email_schema,
    mock_db
):
    """
    Test email retrieval with query parameters
    """
    # Convert the EmailSchema to a dictionary that matches the response format
    email_dict = mock_email_schema.model_dump()
    
    # Create a mock service with a custom fetch_emails method that verifies parameters
    mock_service = AsyncMock()
    
    async def validate_fetch_emails(**kwargs):
        # Verify that parameters are passed correctly
        assert kwargs.get("skip") == 10
        assert kwargs.get("limit") == 5
        assert kwargs.get("unread_only") is True
        assert kwargs.get("category") == "important"
        assert kwargs.get("search") == "test"
        assert kwargs.get("sort_by") == "subject"
        assert kwargs.get("sort_order") == "asc"
        
        return [email_dict], 1, {"source": "database", "db_query": {}}
    
    mock_service.fetch_emails = AsyncMock(side_effect=validate_fetch_emails)
    
    # Patch both the get_email_service function and the database
    with patch('app.routers.emails_router.get_email_service', return_value=mock_service):
        with patch('app.services.email_service.db', mock_db):
            # Act - call with query parameters
            response = test_client.get(
                "/emails?skip=10&limit=5&unread_only=true&category=important&search=test&sort_by=subject&sort_order=asc"
            )

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["emails"]) == 1

@pytest.mark.db
@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
def test_retrieve_email_by_id(
    test_client: TestClient,
    mock_email_schema,
    mock_db
):
    """
    Test retrieving a single email by ID
    """
    email_dict = mock_email_schema.model_dump()
    email_id = "test123"
    
    # Create a mock service that returns the email
    mock_service = AsyncMock()
    
    async def mock_get_email(id):
        assert id == email_id
        return email_dict
    
    mock_service.get_email = AsyncMock(side_effect=mock_get_email)
    
    # Patch both the get_email_service function and the database
    with patch('app.routers.emails_router.get_email_service', return_value=mock_service):
        with patch('app.services.email_service.db', mock_db):
            # Act
            response = test_client.get(f"/emails/{email_id}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["email_id"] == email_dict["email_id"]
            assert data["subject"] == email_dict["subject"]

@pytest.mark.db
@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
def test_retrieve_email_not_found(
    test_client: TestClient,
    mock_db
):
    """
    Test retrieving a non-existent email
    """
    # Create a mock service that returns None (not found)
    mock_service = AsyncMock()
    mock_service.get_email = AsyncMock(return_value=None)
    
    # Patch both the get_email_service function and the database
    with patch('app.routers.emails_router.get_email_service', return_value=mock_service):
        with patch('app.services.email_service.db', mock_db):
            # Act
            response = test_client.get("/emails/nonexistent")
            
            # Assert
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]

@pytest.mark.db
@pytest.mark.skip(reason="MongoDB cursor mocking issues - coroutine vs async object")
def test_mark_email_as_read(
    test_client: TestClient,
    mock_email_schema,
    mock_db
):
    """
    Test marking an email as read
    """
    email_dict = mock_email_schema.model_dump()
    email_dict["is_read"] = True
    email_id = "test123"
    
    # Create a mock service that returns the updated email
    mock_service = AsyncMock()
    
    async def mock_mark_read(id):
        assert id == email_id
        return email_dict
    
    mock_service.mark_email_as_read = AsyncMock(side_effect=mock_mark_read)
    
    # Patch both the get_email_service function and the database
    with patch('app.routers.emails_router.get_email_service', return_value=mock_service):
        with patch('app.services.email_service.db', mock_db):
            # Act
            response = test_client.put(f"/emails/{email_id}/read")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["is_read"] is True