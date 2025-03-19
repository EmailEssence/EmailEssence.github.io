"""
General fixtures for API tests at the root level.

This module ensures proper application initialization for API tests.
"""
import pytest
import os
import sys
from unittest.mock import patch

# Set up environment properly for testing
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/test_db")

@pytest.fixture(scope="session", autouse=True)
def prepare_app():
    """
    Ensure the main app is initialized properly for testing.
    This helps prevent circular import issues.
    """
    # This import should happen only inside this function
    # to avoid circular imports when fixtures are loaded
    from main import app as _app
    
    # Return app for potential use in tests
    return _app
