# uvicorn main:app --reload
import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
import logging

from app.routers import emails_router, summaries_router, auth_router, user_router
from app.services.database import DatabaseConnection
from app.models import EmailSchema, SummarySchema, UserSchema


# from app.models.user_model import User

app = FastAPI(
    title="Email Essence",
    description="A fast, scalable, and secure email summarization service.",
    version="0.1.0",
    # terms_of_service="https://example.com/terms",
    # contact={"name": "Support", "url": "https://example.com/support"},
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",  # Backend default
        "http://localhost:3000",  # Common React dev server
        "http://localhost:5173",  # Vite default
        "http://localhost:4200",  # Angular default
        "http://127.0.0.1:3000",  # React with IP
        "http://127.0.0.1:5173",  # Vite with IP
        "http://127.0.0.1:4200",  # Angular with IP
        "https://emailessence.github.io",
        "https://ee-backend-w86t.onrender.com",  # Your backend deployment URL
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

logger = logging.getLogger(__name__)

async def startup_db_client():
    """
    Initializes MongoDB connection on startup.
    
    This function:
    1. Creates a new database connection
    2. Verifies the connection is alive
    3. Logs available collections
    4. Handles any connection errors gracefully
    """
    try:
        # Initialize database connection
        db = DatabaseConnection()
        await db.connect()
        
        # Verify connection
        await db.client.admin.command('ping')
        logger.info("✅ MongoDB connection established successfully")
        
        # Log available collections
        collections = await db.client.list_collection_names()
        logger.info(f"✅ Available collections: {collections}")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
        raise RuntimeError("Failed to initialize database connection") from e


# Register routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(emails_router, prefix="/emails", tags=["Emails"])
app.include_router(summaries_router, prefix="/summaries", tags=["Summaries"])

# Serve favicon.ico from root directory
@app.get('/favicon.ico')
async def favicon():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    favicon_path = os.path.join(root_dir, 'favicon.ico')
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return HTTPException(status_code=404, detail="Favicon not found")

# Add a health check endpoint for Docker
@app.get("/health", status_code=200)
async def health_check():
    """
    Health check endpoint for monitoring and Docker health checks.
    Verifies core dependencies: MongoDB connection and Google API.
    Returns a 200 OK status if all components are operational.
    """
    health_status = {
        "status": "healthy",
        "components": {
            "database": "unknown",
            "google_api": "unknown"
        }
    }
    
    # Check MongoDB connection
    try:
        await db.command("ping")
        health_status["components"]["database"] = "connected"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Google API connectivity
    try:
        # Use httpx for async HTTP requests
        import httpx
        
        # Check Google OAuth discovery document - this doesn't require authentication
        # and verifies we can reach Google's servers
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get('https://accounts.google.com/.well-known/openid-configuration')
            
            if response.status_code == 200:
                health_status["components"]["google_api"] = "connected"
            else:
                health_status["components"]["google_api"] = f"error: HTTP {response.status_code}"
                health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["components"]["google_api"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status