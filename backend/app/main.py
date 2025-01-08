# uvicorn main:app --reload
from fastapi import FastAPI, HTTPException
from starlette.concurrency import run_in_threadpool

from backend.app.routes.emails_routes import router as emails_router
from backend.app.routes.summaries_routes import router as summaries_router

from backend.app.models.email_model import Email
from backend.app.models.summary_model import EmailSummary
from backend.app.models.user_model import User

app = FastAPI()

# Register routers
app.include_router(emails_router, prefix="/emails", tags=["Emails"])
app.include_router(summaries_router, prefix="/summaries", tags=["Summaries"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

