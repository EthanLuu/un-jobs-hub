"""Metrics and monitoring endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Dict, Any

from database import get_db
from utils.cache import cache, CacheKeys

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Enhanced health check endpoint."""
    try:
        # Check database connection
        result = await db.execute(text("SELECT 1"))
        db_check = result.scalar() == 1
        
        # Get current timestamp
        current_time = datetime.utcnow().isoformat()
        
        return {
            "status": "healthy",
            "timestamp": current_time,
            "database": "connected" if db_check else "disconnected",
            "version": "1.0.0",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get application metrics (cached for 5 minutes)."""
    # Try to get from cache
    cache_key = CacheKeys.metrics()
    cached_metrics = cache.get_json(cache_key)

    if cached_metrics:
        return cached_metrics

    try:
        # Count jobs
        jobs_result = await db.execute(text("SELECT COUNT(*) FROM jobs"))
        jobs_count = jobs_result.scalar()

        # Count users
        users_result = await db.execute(text("SELECT COUNT(*) FROM users"))
        users_count = users_result.scalar()

        # Count favorites
        favorites_result = await db.execute(text("SELECT COUNT(*) FROM favorites"))
        favorites_count = favorites_result.scalar()

        # Count resumes
        resumes_result = await db.execute(text("SELECT COUNT(*) FROM resumes"))
        resumes_count = resumes_result.scalar()

        # Jobs by organization
        orgs_result = await db.execute(
            text("SELECT organization, COUNT(*) as count FROM jobs GROUP BY organization")
        )
        jobs_by_org = {row.organization: row.count for row in orgs_result}

        # Recent jobs (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_result = await db.execute(
            text("SELECT COUNT(*) FROM jobs WHERE last_scraped > :week_ago"),
            {"week_ago": week_ago}
        )
        recent_jobs = recent_result.scalar()

        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "total_jobs": jobs_count,
                "total_users": users_count,
                "total_favorites": favorites_count,
                "total_resumes": resumes_count,
                "recent_jobs_7d": recent_jobs,
                "jobs_by_organization": jobs_by_org,
            },
        }

        # Cache for 5 minutes (300 seconds)
        cache.set_json(cache_key, metrics, ttl=300)

        return metrics

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }

