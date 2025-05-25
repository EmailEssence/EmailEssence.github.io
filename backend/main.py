# uvicorn main:app --reload
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
# Reduce verbosity of httpx and httpcore
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

from app.routers import emails_router, summaries_router, auth_router, user_router
from app.services.database.connection import DatabaseConnection


# from app.models.user_model import User

async def startup_db_client():
    """
    Initializes MongoDB connection and repository indexes on startup.
    """
    try:
        # Get the singleton instance and initialize it
        db = DatabaseConnection()
        await db.initialize()
        
        # Set up repository indexes
        from app.services.database.factories import setup_all_repositories
        await setup_all_repositories()
        logging.info("✅ Database repository indexes set up successfully")
    except Exception as e:
        logging.error(f"❌ Failed to initialize database: {str(e)}")
        raise RuntimeError("Failed to initialize database connection") from e

async def shutdown_db_client():
    """
    Closes MongoDB connection on shutdown.
    """
    try:
        # Get the singleton instance and close it   
        db = DatabaseConnection()
        await db.shutdown()  # Use shutdown instead of close
    except Exception as e:
        raise RuntimeError("Failed to close database connection") from e

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_db_client()
    yield
    await shutdown_db_client()

app = FastAPI(
    title="Email Essence API",
    description="API for the Email Essence application",
    version="0.1.0",
    # terms_of_service="https://example.com/terms",
    # contact={"name": "Support", "url": "https://example.com/support"},
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://emailessence.github.io", # Github Pages
        "https://email.madigan.app", # Personal domain
        "https://ee-backend-w86t.onrender.com", # Backend Render deployment
        "http://localhost:8000",  # Backend default
        "http://localhost:3000",  # Common React dev server
        "http://localhost:5173",  # Vite default
        "http://localhost:4200",  # Angular default
        "http://127.0.0.1:3000",  # React with IP
        "http://127.0.0.1:5173",  # Vite with IP
        "http://127.0.0.1:4200",  # Angular with IP
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# API Route Handlers (definitions moved before router inclusions)
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that returns basic API information.
    Useful for users and systems that discover the API.
    """
    return {
        "name": "Email Essence API",
        "version": app.version,
        "description": "API for summarizing and managing email content",
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "endpoints": [
            {"path": "/auth", "description": "Authentication operations"},
            {"path": "/user", "description": "User profile management"},
            {"path": "/emails", "description": "Email retrieval and management"},
            {"path": "/summaries", "description": "Email summarization"}
        ],
        "status": "online"
    }

# Serve favicon.ico from root directory - only served to swagger UI
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
        db = DatabaseConnection()
        await db.command("ping")
        health_status["components"]["database"] = "connected"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Google API connectivity
    try:
        # Use httpx for async HTTP requests
        import httpx
        
        logger.info("Checking Google API connectivity...")
        # Check Google OAuth discovery document - this doesn't require authentication
        # and verifies we can reach Google's servers
        async with httpx.AsyncClient(timeout=5.0) as client:
            logger.debug("Making request to Google OAuth discovery endpoint")
            response = await client.get('https://accounts.google.com/.well-known/openid-configuration')
            
            if response.status_code == 200:
                logger.info("✅ Google API connectivity check successful")
                health_status["components"]["google_api"] = "connected"
            else:
                logger.error(f"❌ Google API connectivity check failed with status {response.status_code}")
                health_status["components"]["google_api"] = f"error: HTTP {response.status_code}"
                health_status["status"] = "unhealthy"
    except Exception as e:
        logger.error(f"❌ Google API connectivity check failed with error: {str(e)}")
        health_status["components"]["google_api"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status

# Register Routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(emails_router, prefix="/emails", tags=["Emails"])
app.include_router(summaries_router, prefix="/summaries", tags=["Summaries"])