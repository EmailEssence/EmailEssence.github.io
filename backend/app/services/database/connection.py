from contextlib import asynccontextmanager
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.config import Settings, get_settings

class DatabaseConnection:
    """
    Manages MongoDB database connections.
    Uses context managers for proper resource management.
    """
    def __init__(self, mongo_uri: str = None):
        settings = get_settings()
        self.mongo_uri = mongo_uri or settings.mongo_uri
        self._client = None
        self._db = None

    async def connect(self):
        """Establish database connection"""
        if not self._client:
            self._client = AsyncIOMotorClient(self.mongo_uri)
            self._db = self._client.email_system

    async def disconnect(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

    @property
    def client(self) -> AsyncIOMotorClient:
        """Get MongoDB client instance"""
        if not self._client:
            raise RuntimeError("Database not connected")
        return self._client

    @property
    def db(self):
        """Get database instance"""
        if not self._db:
            raise RuntimeError("Database not connected")
        return self._db

    @property
    def emails(self):
        """Get emails collection"""
        return self.db.emails

    @property
    def users(self):
        """Get users collection"""
        return self.db.users

    @property
    def summaries(self):
        """Get summaries collection"""
        return self.db.summaries

@asynccontextmanager
async def get_database_connection(mongo_uri: str = None) -> AsyncGenerator[DatabaseConnection, None]:
    """
    Context manager for database connections.
    Ensures proper connection cleanup.
    """
    connection = DatabaseConnection(mongo_uri)
    try:
        await connection.connect()
        yield connection
    finally:
        await connection.disconnect() 