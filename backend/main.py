# uvicorn main:app --reload
from fastapi import FastAPI, HTTPException
from starlette.concurrency import run_in_threadpool

from app.routers.emails_router import router as emails_router
from app.routers.summaries_router import router as summaries_router
from app.routers.auth_router import router as auth_router

from app.models.email_model import Email
from app.models.summary_model import EmailSummary
# from app.models.user_model import User

app = FastAPI()

# Register routers
app.include_router(emails_router, prefix="/emails", tags=["Emails"])
app.include_router(summaries_router, prefix="/summaries", tags=["Summaries"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

