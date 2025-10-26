"""Main FastAPI application entry point."""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config import settings
from database import get_engine, Base
from routers import auth, jobs, favorites, resume, match, metrics
from utils.monitoring import setup_monitoring
from utils.exceptions import setup_exception_handlers
from utils.logger import setup_logger
from utils.config_validator import ConfigValidator
from utils.rate_limit import RateLimitMiddleware
# from routers import crawl  # Disabled for quick start

# Setup logging
logger = setup_logger(__name__, level=settings.log_level)

# Check if running in serverless environment
is_serverless = os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    # Validate configuration (non-strict in serverless)
    if not is_serverless:
        ConfigValidator.run_startup_checks(strict=True)

    engine = get_engine()
    if not is_serverless:
        # Only create tables in non-serverless environments
        # In serverless, tables should be created via migrations
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

    logger.info(f"{settings.app_name} started successfully")
    yield

    # Shutdown
    logger.info("Shutting down application...")
    await engine.dispose()
    logger.info("Application shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="UN Jobs Hub API - Aggregating job postings from UN organizations",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
)

# Setup exception handlers
setup_exception_handlers(app)

# Setup monitoring and logging
setup_monitoring(app)

# Setup rate limiting (before CORS)
if settings.environment == "production":
    # Stricter limits in production
    app.add_middleware(
        RateLimitMiddleware,
        default_limit=100,
        default_window=60,
        enable_cleanup=True
    )
else:
    # Generous limits in development
    app.add_middleware(
        RateLimitMiddleware,
        default_limit=1000,
        default_window=60,
        enable_cleanup=True
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
app.include_router(metrics.router, prefix="/api", tags=["Metrics"])
# app.include_router(crawl.router, prefix="/api/crawl", tags=["Crawler"])  # Disabled for quick start


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to UNJobsHub API",
        "version": settings.app_version,
        "docs": "/docs"
    }




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

