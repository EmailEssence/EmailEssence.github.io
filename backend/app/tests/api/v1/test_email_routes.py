# tests/api/v1/test_email_routes.py
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

@pytest.mark.db
@pytest.mark.asyncio
async def test_retrieve_emails_success(
    test_client: TestClient,
    mock_email_schema
):
    """
    Test successful email retrieval flow
    """
    # Convert the EmailSchema to a dictionary that matches the response format
    email_dict = mock_email_schema.model_dump()
    
    # Create a mock function that returns the expected tuple format
    async def mock_fetch_emails(**kwargs):
        return [email_dict], 1, {"source": "database", "db_query": {}}
    
    custom_mock = AsyncMock(side_effect=mock_fetch_emails)
    
    # Patch the service function with our custom mock
    with patch('app.routers.emails_router.email_service.fetch_emails', custom_mock):
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
async def test_retrieve_emails_empty(
    test_client: TestClient
):
    """
    Test behavior when no emails are found
    """
    # Create a mock function that returns empty results
    async def mock_empty_fetch_emails(**kwargs):
        return [], 0, {"source": "database", "db_query": {}}
    
    mock_empty_fetch_emails = AsyncMock(side_effect=mock_empty_fetch_emails)
    
    # Patch the service function
    with patch('app.routers.emails_router.email_service.fetch_emails', mock_empty_fetch_emails):
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
async def test_retrieve_emails_service_error(
    test_client: TestClient
):
    """
    Test error handling when email service fails
    """
    # Create a mock function that raises an exception
    async def mock_error_fetch_emails(**kwargs):
        raise HTTPException(status_code=500, detail="IMAP connection failed")
    
    mock_error_fetch_emails = AsyncMock(side_effect=mock_error_fetch_emails)
    
    # Patch the service function to raise an exception
    with patch('app.routers.emails_router.email_service.fetch_emails', mock_error_fetch_emails):
        # Act
        response = test_client.get("/emails")

        # Assert
        assert response.status_code == 500
        assert "IMAP connection failed" in response.json()["detail"]

@pytest.mark.db
@pytest.mark.asyncio
async def test_retrieve_emails_with_filters(
    test_client: TestClient,
    mock_email_schema
):
    """
    Test email retrieval with query parameters
    """
    # Convert the EmailSchema to a dictionary that matches the response format
    email_dict = mock_email_schema.model_dump()
    
    # Create a mock function that returns the expected tuple format
    async def mock_fetch_emails(**kwargs):
        # Verify that parameters are passed correctly
        assert kwargs.get("skip") == 10
        assert kwargs.get("limit") == 5
        assert kwargs.get("unread_only") is True
        assert kwargs.get("category") == "important"
        assert kwargs.get("search") == "test"
        assert kwargs.get("sort_by") == "subject"
        assert kwargs.get("sort_order") == "asc"
        
        return [email_dict], 1, {"source": "database", "db_query": {}}
    
    custom_mock = AsyncMock(side_effect=mock_fetch_emails)
    
    # Patch the service function with our custom mock
    with patch('app.routers.emails_router.email_service.fetch_emails', custom_mock):
        # Act - call with query parameters
        response = test_client.get(
            "/emails?skip=10&limit=5&unread_only=true&category=important&search=test&sort_by=subject&sort_order=asc"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["emails"]) == 1

@pytest.mark.db
def test_retrieve_email_by_id(
    test_client: TestClient,
    mock_email_schema
):
    """
    Test retrieving a single email by ID
    """
    email_dict = mock_email_schema.model_dump()
    email_id = "test123"
    
    # Create a mock function for fetch_email
    async def mock_fetch_email(id):
        assert id == email_id
        return email_dict
    
    with patch('app.routers.emails_router.email_service.fetch_email', 
               AsyncMock(side_effect=mock_fetch_email)):
        # Act
        response = test_client.get(f"/emails/{email_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email_id"] == email_dict["email_id"]
        assert data["subject"] == email_dict["subject"]

@pytest.mark.db
def test_retrieve_email_not_found(
    test_client: TestClient
):
    """
    Test retrieving a non-existent email
    """
    # Mock fetch_email to return None (not found)
    with patch('app.routers.emails_router.email_service.fetch_email', 
               AsyncMock(return_value=None)):
        # Act
        response = test_client.get("/emails/nonexistent")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

@pytest.mark.db
def test_mark_email_as_read(
    test_client: TestClient,
    mock_email_schema
):
    """
    Test marking an email as read
    """
    email_dict = mock_email_schema.model_dump()
    email_dict["is_read"] = True
    email_id = "test123"
    
    # Create a mock function for mark_email_as_read
    async def mock_mark_read(id):
        assert id == email_id
        return email_dict
    
    with patch('app.routers.emails_router.email_service.mark_email_as_read', 
               AsyncMock(side_effect=mock_mark_read)):
        # Act
        response = test_client.put(f"/emails/{email_id}/read")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["is_read"] is True