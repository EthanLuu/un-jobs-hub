"""Main FastAPI application entry point."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config import settings
from database import engine, Base
from routers import auth, jobs, favorites, resume, match
# from routers import crawl  # Disabled for quick start


# Check if running in serverless environment
is_serverless = os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    if not is_serverless:
        # Only create tables in non-serverless environments
        # In serverless, tables should be created via migrations
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(match.router, prefix="/api/match", tags=["Matching"])
# app.include_router(crawl.router, prefix="/api/crawl", tags=["Crawler"])  # Disabled for quick start


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to UNJobsHub API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={"status": "healthy", "service": settings.app_name},
        status_code=200
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

