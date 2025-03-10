"""
Root level pytest configuration to ensure test settings are applied
before any other imports happen.
"""
import os
import pytest
import sys
from unittest.mock import patch

# Load test environment as early as possible
os.environ.setdefault("ENVIRONMENT", "testing")

# Create mock values for required settings
test_env_values = {
    "GOOGLE_CLIENT_ID": "test-client-id",
    "GOOGLE_CLIENT_SECRET": "test-client-secret",
    "EMAIL_ACCOUNT": "test@example.com",
    "MONGO_URI": "mongodb://localhost:27017/test_db",
    "OPENAI_API_KEY": "sk-test-key-123456789"
}

# Apply these test values to os.environ
for key, value in test_env_values.items():
    if key not in os.environ:
        os.environ[key] = value

# Automatically skip database tests
def pytest_configure(config):
    """Configure pytest with custom markers and skip logic"""
    # Register database marker
    config.addinivalue_line("markers", "db: Tests that interact with the database")
    
    # Check if we should skip database tests (default is True in CI environment)
    if os.environ.get("SKIP_DB_TESTS", "1") == "1":
        # Register a marker to skip all database tests
        config.addinivalue_line("markers", 
            "skip_db: Skip database tests automatically")
        
        # Add skipif condition for db tests
        config.addinivalue_line("markers",
            'skipif("True", reason="Database tests are disabled")')

def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip database tests"""
    if os.environ.get("SKIP_DB_TESTS", "1") == "1":
        skip_db = pytest.mark.skip(reason="Database tests disabled")
        for item in items:
            if "db" in item.keywords:
                item.add_marker(skip_db)

# Patch sys.modules to use our mock database
# This prevents the actual database.py from being imported
@pytest.fixture(scope="session", autouse=True)
def patch_modules():
    """Patch system modules to use test mocks"""
    # Path to our mock module
    from app.tests.database_mock import db as mock_db
    
    # Create a mock module for 'database'
    class MockDatabaseModule:
        db = mock_db
    
    # Patch the database module
    sys.modules['database'] = MockDatabaseModule
    
    yield
    
    # Clean up after tests
    if 'database' in sys.modules:
        del sys.modules['database']

# Ensure test settings are used
@pytest.fixture(scope="session", autouse=True)
def patch_settings():
    """Patch the get_settings function to use test settings"""
    from app.tests.test_config import override_get_settings
    from app.utils.config import get_settings
    
    with patch('app.utils.config.get_settings', override_get_settings):
        yield 