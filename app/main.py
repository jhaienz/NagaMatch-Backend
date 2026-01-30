from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import init_db
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting NagaMatch API...")

    # Ensure directories exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)

    # Initialize database tables
    await init_db()
    print("Database initialized")

    yield

    # Shutdown
    print("Shutting down NagaMatch API...")


app = FastAPI(
    title=settings.app_name,
    description="""
    ## NagaMatch API

    AI-powered employment matching platform for Naga City.

    ### Features
    - **Resume Processing**: Upload PDF resumes and extract information using NLP
    - **AI Matching**: Match job seekers to relevant opportunities using vector similarity
    - **Job Management**: Create and manage job postings
    - **Application Tracking**: Track job applications and their status

    ### How it works
    1. Upload a resume (PDF) → AI extracts skills, experience, education
    2. Create job postings with requirements
    3. Get AI-powered matches between resumes and jobs
    4. Apply to jobs with automatic match scoring
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "AI-powered employment matching platform",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
