from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

client = AsyncIOMotorClient(MONGO_URI)
db = client.email_system