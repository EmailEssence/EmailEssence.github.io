from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.config import Settings, get_settings
from motor.motor_asyncio import AsyncIOMotorClient

settings = get_settings()

client = AsyncIOMotorClient(settings.mongo_uri)
db = client.email_system