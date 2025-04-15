"""
Database connection management.
"""

from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient
import logging

from app.utils.config import get_settings

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Manages MongoDB database connections.
    """
    
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    async def initialize(self):
        """
        Initialize the database connection asynchronously.
        Verifies the connection is alive and logs available collections.
        """
        if self._client is None:
            try:
                settings = get_settings()
                self._client = AsyncIOMotorClient(settings.mongo_uri)
                self._db = self._client.email_essence
                
                # Verify connection
                await self._client.admin.command('ping')
                logger.info("✅ MongoDB connection established successfully")
                
                # Log available collections
                collections = await self._db.list_collection_names()
                logger.info(f"✅ Available collections: {collections}")
                
            except Exception as e:
                logger.error(f"❌ Failed to connect to MongoDB: {e}")
                raise

    @property
    def client(self):
        """
        Get the MongoDB client instance.
        
        Returns:
            AsyncIOMotorClient: MongoDB client instance
        """
        if self._client is None:
            raise RuntimeError("Database not connected")
        return self._client

    @property
    def db(self):
        """
        Get the database instance.
        
        Returns:
            Database: MongoDB database instance
        """
        if self._db is None:
            raise RuntimeError("Database not connected")
        return self._db

    async def close(self):
        """
        Close the database connection.
        """
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("Disconnected from MongoDB")

# Create a single instance
instance = DatabaseConnection() 