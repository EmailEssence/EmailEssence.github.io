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
from app.services.database import (
    EmailRepository,
    UserRepository,
    SummaryRepository,
    TokenRepository
)

from .constants import EMAIL_DATA, USER_DATA, TOKEN_DATA, SUMMARY_DATA


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
        self.insert_many = AsyncMock(return_value=MagicMock())
        self.update_one = AsyncMock(return_value=MagicMock())
        self.delete_one = AsyncMock(return_value=MagicMock())
        self.count_documents = AsyncMock(return_value=len(self.test_data))
        self.create_index = AsyncMock()
        self.find_one_and_update = AsyncMock()
        self.find_one_and_delete = AsyncMock()
        self.aggregate = AsyncMock()
        self.bulk_write = AsyncMock(return_value=MagicMock())
        
        # Set returns for common operations
        self.insert_one.return_value.inserted_id = "mock_id"
        self.update_one.return_value.modified_count = 1
        self.update_one.return_value.upserted_id = None
        self.delete_one.return_value.deleted_count = 1
        self.insert_many.return_value.inserted_ids = ["mock_id_1", "mock_id_2"]
        self.bulk_write.return_value.upserted_count = 2
        self.bulk_write.return_value.modified_count = 3
        
        # Setup for find methods
        self._setup_find()
    
    def _setup_find(self):
        """Setup the find method to return a proper cursor."""
        def mock_find(query=None, **kwargs):
            # Filter data based on the query if needed for tests
            result = self.test_data
            if query:
                result = [doc for doc in result if all(doc.get(k) == v for k, v in query.items())]
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
        
        # Configure update_one to return modified_count=0 for non-existent documents
        async def mock_update_one(filter, update, **kwargs):
            # Check if document exists in test data
            exists = any(all(doc.get(k) == v for k, v in filter.items()) for doc in self.test_data)
            if not exists:
                self.update_one.return_value.modified_count = 0
            else:
                self.update_one.return_value.modified_count = 1
            return self.update_one.return_value
        self.update_one.side_effect = mock_update_one
    
    def configure_delete_result(self, deleted_count=1):
        """Configure delete_one return values."""
        self.delete_one.return_value.deleted_count = deleted_count
        
        # Configure delete_one to return deleted_count=0 for non-existent documents
        async def mock_delete_one(filter):
            # Check if document exists in test data
            exists = any(all(doc.get(k) == v for k, v in filter.items()) for doc in self.test_data)
            if not exists:
                self.delete_one.return_value.deleted_count = 0
            else:
                self.delete_one.return_value.deleted_count = 1
            return self.delete_one.return_value
        self.delete_one.side_effect = mock_delete_one


# Create mock database
mock_db = MagicMock(spec=AsyncIOMotorDatabase)

# Add collections to the mock database
mock_db.emails = MockCollection("emails", EMAIL_DATA)
mock_db.users = MockCollection("users", USER_DATA)
mock_db.tokens = MockCollection("tokens", TOKEN_DATA)
mock_db.summaries = MockCollection("summaries", SUMMARY_DATA)

# Configure specific behavior for emails collection
mock_db.emails.configure_find_one({
    "email_id": {"value": "test_1", "result": EMAIL_DATA[0]},
    "google_id": {"value": "user123", "result": EMAIL_DATA[0]}
})
mock_db.emails.configure_update_result()
mock_db.emails.configure_delete_result()

# Configure specific behavior for users collection
mock_db.users.configure_find_one({
    "google_id": {"value": "user123", "result": USER_DATA[0]},
    "email": {"value": "user@example.com", "result": USER_DATA[0]}
})
mock_db.users.configure_update_result()
mock_db.users.configure_delete_result()

# Configure specific behavior for tokens collection
mock_db.tokens.configure_find_one({
    "google_id": {"value": "user123", "result": TOKEN_DATA[0]},
    "token": {"value": "access_token_123", "result": TOKEN_DATA[0]}
})
mock_db.tokens.configure_update_result()
mock_db.tokens.configure_delete_result()

# Configure specific behavior for summaries collection
mock_db.summaries.configure_find_one({
    "email_id": {"value": "test_1", "result": SUMMARY_DATA[0]},
    "google_id": {"value": "user123", "result": SUMMARY_DATA[0]}
})
mock_db.summaries.configure_update_result()
mock_db.summaries.configure_delete_result()


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