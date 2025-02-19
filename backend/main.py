# uvicorn main:app --reload
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from app.routers import emails_router, summaries_router, auth_router, user_router
from app.models import EmailSchema, SummarySchema, UserSchema
from database import db  


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
        "http://localhost:8000",
        "https://emailessence.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.on_event("startup")
async def startup_db_client():
    print("Connecting to MongoDB...")
    try:
        await db.command("ping")  
        collections = await db.list_collection_names()
        print(f"✅ Collections in DB: {collections}")

        print("MongoDB connection successful!")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {str(e)}")


# Register routers
app.include_router(emails_router, prefix="/emails", tags=["Emails"])
app.include_router(summaries_router, prefix="/summaries", tags=["Summaries"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# Serve favicon.ico from root directory
@app.get('/favicon.ico')
async def favicon():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    favicon_path = os.path.join(root_dir, 'favicon.ico')
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return HTTPException(status_code=404, detail="Favicon not found")