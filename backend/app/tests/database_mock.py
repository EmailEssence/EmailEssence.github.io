"""
Mock database for testing purposes.

This module provides mock objects for MongoDB database operations,
specifically designed to work with our repository pattern.
"""
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, List, Any, Optional, Type
from datetime import datetime

import pytest
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.models.email_models import EmailSchema
from app.models.user_models import UserSchema
from app.models.summary_models import SummarySchema
from app.models.auth_models import TokenData
from app.services.database.email_repository import EmailRepository
from app.services.database.user_repository import UserRepository
from app.services.database.summary_repository import SummaryRepository
from app.services.database.token_repository import TokenRepository


class MockCursor:
    """
    Mock MongoDB cursor that properly implements cursor methods.
    """
    def __init__(self, data=None):
        self.data = data or []
        self.skip_val = 0
        self.limit_val = None
        self.sort_spec = None
        
    async def to_list(self, length=None):
        """Convert cursor results to a list."""
        result = self.data
        
        # Apply pagination if needed
        if self.skip_val > 0:
            result = result[self.skip_val:]
        
        if self.limit_val is not None:
            result = result[:self.limit_val]
            
        # Here we could implement sorting based on self.sort_spec
        # if needed for tests
            
        return result
    
    def sort(self, key_or_list, direction=None):
        """Mock sort method."""
        self.sort_spec = (key_or_list, direction)
        return self
    
    def skip(self, skip):
        """Mock skip method."""
        self.skip_val = skip
        return self
        
    def limit(self, limit):
        """Mock limit method."""
        self.limit_val = limit
        return self


class MockCollection:
    """Mock MongoDB collection with async methods."""
    
    def __init__(self, name, test_data=None):
        self.name = name
        self.test_data = test_data or []
        
        # Async operations
        self.find_one = AsyncMock(return_value=None)
        self.insert_one = AsyncMock(return_value=MagicMock())
        self.update_one = AsyncMock(return_value=MagicMock())
        self.delete_one = AsyncMock(return_value=MagicMock())
        self.count_documents = AsyncMock(return_value=len(self.test_data))
        self.create_index = AsyncMock()
        self.find_one_and_update = AsyncMock()
        self.find_one_and_delete = AsyncMock()
        self.aggregate = AsyncMock()
        
        # Set returns for common operations
        self.insert_one.return_value.inserted_id = "mock_id"
        self.update_one.return_value.modified_count = 1
        self.update_one.return_value.upserted_id = None
        self.delete_one.return_value.deleted_count = 1
        
        # Setup for find methods
        self._setup_find()
    
    def _setup_find(self):
        """Setup the find method to return a proper cursor."""
        def mock_find(query=None, **kwargs):
            # Filter data based on the query if needed for tests
            result = self.test_data
            return MockCursor(result)
            
        self.find = MagicMock(side_effect=mock_find)
    
    def configure_find_one(self, query_result_map: Dict[str, Any]):
        """
        Configure find_one to return specific results for specific queries.
        
        Args:
            query_result_map: Dict mapping query key-value pairs to result documents
        """
        async def mock_find_one(query):
            # Handle _id conversion to ObjectId
            if '_id' in query and not isinstance(query['_id'], ObjectId):
                try:
                    if ObjectId.is_valid(query['_id']):
                        # For tests, we'll just pretend we did the conversion
                        pass
                    else:
                        # Simulate MongoDB's behavior with invalid IDs
                        raise ValueError(f"{query['_id']} is not a valid ObjectId")
                except Exception:
                    raise ValueError(f"{query['_id']} is not a valid ObjectId")
            
            for key, value in query.items():
                if key in query_result_map and value == query_result_map[key]["value"]:
                    return query_result_map[key]["result"]
            return None
            
        self.find_one.side_effect = mock_find_one
    
    def configure_update_result(self, modified_count=1, upserted_id=None):
        """Configure update_one return values."""
        self.update_one.return_value.modified_count = modified_count
        self.update_one.return_value.upserted_id = upserted_id


# Create mock database
mock_db = MagicMock(spec=AsyncIOMotorDatabase)

# Sample data for email collection
email_data = [
    {
        "email_id": "test_1",
        "google_id": "user123",
        "sender": "test@example.com",
        "recipients": ["recipient@example.com"],
        "subject": "Test Email 1",
        "body": "This is a test email body",
        "received_at": "2023-01-01T00:00:00Z",
        "category": "inbox",
        "is_read": False
    },
    {
        "email_id": "test_2",
        "google_id": "user123",
        "sender": "another@example.com",
        "recipients": ["recipient@example.com"],
        "subject": "Test Email 2",
        "body": "This is another test email body",
        "received_at": "2023-01-02T00:00:00Z",
        "category": "inbox",
        "is_read": True
    }
]

# Sample data for user collection
user_data = [
    {
        "google_id": "user123",
        "email": "user@example.com",
        "name": "Test User",
        "picture": "https://example.com/pic.jpg",
        "preferences": {
            "theme": "dark",
            "emails_per_page": 25
        }
    }
]

# Sample data for token collection
token_data = [
    {
        "google_id": "user123",
        "token": "access_token_123",
        "refresh_token": "refresh_token_123",
        "token_type": "Bearer",
        "expiry": "2023-12-31T23:59:59Z"
    }
]

# Sample data for summary collection
summary_data = [
    {
        "email_id": "test_1",
        "google_id": "user123",
        "summary": "This is a test summary",
        "keywords": ["test", "email"],
        "generated_at": "2023-01-01T01:00:00Z",
        "model": "test-model"
    }
]

# Add collections to the mock database
mock_db.emails = MockCollection("emails", email_data)
mock_db.users = MockCollection("users", user_data)
mock_db.tokens = MockCollection("tokens", token_data)
mock_db.summaries = MockCollection("summaries", summary_data)

# Configure specific behavior for emails collection
mock_db.emails.configure_find_one({
    "email_id": {"value": "test_1", "result": email_data[0]},
    "google_id": {"value": "user123", "result": email_data[0]}
})

# Configure specific behavior for users collection
mock_db.users.configure_find_one({
    "google_id": {"value": "user123", "result": user_data[0]},
    "email": {"value": "user@example.com", "result": user_data[0]}
})

# Configure specific behavior for tokens collection
mock_db.tokens.configure_find_one({
    "google_id": {"value": "user123", "result": token_data[0]},
    "token": {"value": "access_token_123", "result": token_data[0]}
})

# Configure specific behavior for summaries collection
mock_db.summaries.configure_find_one({
    "email_id": {"value": "test_1", "result": summary_data[0]},
    "google_id": {"value": "user123", "result": summary_data[0]}
})


@pytest.fixture
def mock_email_collection():
    """Return a mock email collection for testing."""
    return mock_db.emails


@pytest.fixture
def mock_user_collection():
    """Return a mock user collection for testing."""
    return mock_db.users


@pytest.fixture
def mock_token_collection():
    """Return a mock token collection for testing."""
    return mock_db.tokens


@pytest.fixture
def mock_summary_collection():
    """Return a mock summary collection for testing."""
    return mock_db.summaries


@pytest.fixture
def mock_email_repository(mock_email_collection):
    """Return an EmailRepository with a mock collection."""
    return EmailRepository(mock_email_collection)


@pytest.fixture
def mock_user_repository(mock_user_collection):
    """Return a UserRepository with a mock collection."""
    return UserRepository(mock_user_collection)


@pytest.fixture
def mock_token_repository(mock_token_collection):
    """Return a TokenRepository with a mock collection."""
    return TokenRepository(mock_token_collection)


@pytest.fixture
def mock_summary_repository(mock_summary_collection):
    """Return a SummaryRepository with a mock collection."""
    return SummaryRepository(mock_summary_collection) 