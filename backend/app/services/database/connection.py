"""
Database connection management.
"""

from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

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
                
                # Configure connection options
                connection_options = {
                    "serverSelectionTimeoutMS": 5000,  # 5 second timeout
                    "connectTimeoutMS": 10000,        # 10 second connection timeout
                    "retryWrites": True,              # Enable retryable writes
                    "retryReads": True,               # Enable retryable reads
                }
                
                self._client = AsyncIOMotorClient(
                    settings.mongo_uri,
                    **connection_options
                )
                self._db = self._client.email_essence
                
                # Verify connection with timeout
                try:
                    logger.info("🔍 Attempting to connect to MongoDB...")
                    await self._client.admin.command('ping')
                    logger.info("✅ MongoDB connection established successfully")
                except ServerSelectionTimeoutError:
                    logger.error("❌ MongoDB server selection timeout - server not available")
                    raise
                except ConnectionFailure:
                    logger.error("❌ MongoDB connection failure - could not connect to server")
                    raise
                
                # Log available collections
                collections = await self._db.list_collection_names()
                logger.info(f"✅ Available collections: {collections}")
                
            except Exception as e:
                logger.error(f"❌ Failed to connect to MongoDB: {e}")
                # Clean up on failure
                if self._client:
                    self._client.close()
                    self._client = None
                    self._db = None
                raise

    async def shutdown(self):
        """
        Shutdown the database connection asynchronously.
        """
        if self._client is not None:
            try:
                self._client.close()  # Note: Motor's close() method is not a coroutine
                self._client = None
                self._db = None
                logger.info("✅ Disconnected from MongoDB")
            except Exception as e:
                logger.error(f"❌ Failed to disconnect from MongoDB: {e}")
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

# Create a single instance
instance = DatabaseConnection() 