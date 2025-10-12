"""Crawler management routes (admin only)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User
from utils.auth import get_current_admin_user
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



