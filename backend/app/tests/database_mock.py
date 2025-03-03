"""
Mock database module for testing to avoid direct MongoDB dependency
"""
from unittest.mock import AsyncMock

# Create a mock database object that doesn't require actual MongoDB connection
class MockDatabase:
    def __init__(self):
        self.emails = AsyncMock()
        self.emails.find = AsyncMock()
        self.emails.find_one = AsyncMock()
        self.emails.insert_one = AsyncMock()
        self.emails.update_one = AsyncMock()
        self.emails.delete_one = AsyncMock()
        
        # Add other collections as needed
        self.summaries = AsyncMock()
        self.users = AsyncMock()
        
    def configure_cursor(self, collection_name, data=None):
        """Configure a collection's find() method to return a proper cursor"""
        data = data or []
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=data)
        
        getattr(self, collection_name).find.return_value = mock_cursor
        return mock_cursor

# Create singleton instance
db = MockDatabase() 