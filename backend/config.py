import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
