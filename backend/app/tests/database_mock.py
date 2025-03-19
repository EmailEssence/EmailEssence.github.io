"""
Mock database for testing purposes.

This module provides mock objects for MongoDB database operations.
"""
from unittest.mock import MagicMock, AsyncMock

class MockCollection:
    """Mock MongoDB collection with async methods."""
    
    def __init__(self, name, test_data=None):
        self.name = name
        self.test_data = test_data or []
        
        # Async operations
        self.find_one = AsyncMock(return_value=None)
        self.insert_one = AsyncMock()
        self.update_one = AsyncMock()
        self.delete_one = AsyncMock()
        self.count_documents = AsyncMock(return_value=0)
        
        # Setup for find methods
        self._setup_find()
    
    def _setup_find(self):
        """Setup the find method and its chain of methods."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=self.test_data)
        
        # Create the chain of methods
        mock_skip = AsyncMock()
        mock_skip.limit = AsyncMock(return_value=mock_cursor)
        
        mock_sort = AsyncMock()
        mock_sort.skip = AsyncMock(return_value=mock_skip)
        
        self.find = AsyncMock(return_value=mock_sort)

# Create mock database
db = MagicMock()

# Add collections
db.emails = MockCollection("emails", [
    {
        "email_id": "test_1",
        "user_id": "test_user",
        "sender": "test@example.com",
        "recipients": ["recipient@example.com"],
        "subject": "Test Email",
        "body": "This is a test email body",
        "received_at": "2023-01-01T00:00:00Z",
        "category": "inbox",
        "is_read": False
    }
])

# Setup specific return values for commonly used queries
db.emails.find_one.return_value = {
    "email_id": "test_1",
    "user_id": "test_user",
    "sender": "test@example.com",
    "recipients": ["recipient@example.com"],
    "subject": "Test Email",
    "body": "This is a test email body",
    "received_at": "2023-01-01T00:00:00Z",
    "category": "inbox",
    "is_read": False
}

# Count documents
db.emails.count_documents.return_value = 1

# Update operations
update_result = MagicMock()
update_result.matched_count = 1
db.emails.update_one.return_value = update_result

# Delete operations
delete_result = MagicMock()
delete_result.deleted_count = 1
db.emails.delete_one.return_value = delete_result

# Add other collections as needed
db.summaries = AsyncMock()
db.users = AsyncMock() 