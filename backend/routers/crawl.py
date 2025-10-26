"""Crawler management routes (admin only)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from models.user import User
from utils.auth import get_current_admin_user
from utils.crawler_monitoring import crawler_monitor
from celery_app import crawl_un_careers, crawl_undp_jobs

router = APIRouter()


@router.post("/trigger")
async def trigger_crawl(
    organization: str,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger a crawl task (admin only)."""
    crawlers = {
        "un": crawl_un_careers,
        "undp": crawl_undp_jobs,
    }
    
    if organization not in crawlers:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown organization. Available: {', '.join(crawlers.keys())}"
        )
    
    # Trigger Celery task
    task = crawlers[organization].delay()
    
    return {
        "message": f"Crawl task triggered for {organization}",
        "task_id": task.id,
        "status": "queued"
    }


@router.get("/status/{task_id}")
async def get_crawl_status(
    task_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get crawl task status (admin only)."""
    from celery.result import AsyncResult
    
    task = AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task.state,
        "result": task.result if task.ready() else None
    }


@router.post("/trigger-all")
async def trigger_all_crawls(
    current_user: User = Depends(get_current_admin_user)
):
    """Trigger all crawler tasks (admin only)."""
    tasks = []
    
    # Trigger all crawlers
    task_un = crawl_un_careers.delay()
    tasks.append({"organization": "un", "task_id": task_un.id})
    
    task_undp = crawl_undp_jobs.delay()
    tasks.append({"organization": "undp", "task_id": task_undp.id})
    
    return {
        "message": "All crawl tasks triggered",
        "tasks": tasks
    }


@router.get("/health")
async def get_crawler_health_overview(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get health overview for all crawlers (admin only).

    Returns overall health status and summary statistics.
    """
    overall_health = crawler_monitor.get_overall_health()
    all_health = crawler_monitor.get_all_health()

    return {
        "overall": overall_health,
        "crawlers": all_health
    }


@router.get("/health/{organization}")
async def get_specific_crawler_health(
    organization: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get detailed health status for a specific crawler (admin only).

    Args:
        organization: Organization name

    Returns:
        Detailed health information including checks and statistics
    """
    health = crawler_monitor.get_crawler_health(organization)

    if health["health"] == "unknown":
        raise HTTPException(
            status_code=404,
            detail=f"No data available for organization: {organization}"
        )

    return health


@router.get("/stats")
async def get_crawler_stats(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get statistics for all crawlers (admin only).

    Returns aggregated statistics across all crawlers.
    """
    all_health = crawler_monitor.get_all_health()

    total_runs = sum(c["stats"]["total_runs"] for c in all_health)
    total_jobs_found = sum(c["stats"]["total_jobs_found"] for c in all_health)
    total_jobs_saved = sum(c["stats"]["total_jobs_saved"] for c in all_health)

    return {
        "total_crawlers": len(all_health),
        "total_runs": total_runs,
        "total_jobs_found": total_jobs_found,
        "total_jobs_saved": total_jobs_saved,
        "crawlers": [
            {
                "organization": c["organization"],
                "total_runs": c["stats"]["total_runs"],
                "success_rate": c["stats"]["success_rate"],
                "total_jobs_found": c["stats"]["total_jobs_found"],
                "total_jobs_saved": c["stats"]["total_jobs_saved"],
                "average_duration": c["stats"]["average_duration"],
                "last_run": c["stats"]["last_run"],
                "health": c["health"]
            }
            for c in all_health
        ]
    }



