"""Job listing routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional

from database import get_db
from models.job import Job
from models.user import User
from schemas.job import JobResponse, JobFilter
from utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=dict)
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    organization: Optional[str] = None,
    category: Optional[str] = None,
    grade: Optional[str] = None,
    location: Optional[str] = None,
    keywords: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List jobs with filtering and pagination."""
    # Build query
    query = select(Job).where(Job.is_active == True)
    
    if organization:
        query = query.where(Job.organization == organization)
    
    if category:
        query = query.where(Job.category == category)
    
    if grade:
        query = query.where(Job.grade == grade)
    
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))
    
    if keywords:
        search_pattern = f"%{keywords}%"
        query = query.where(
            or_(
                Job.title.ilike(search_pattern),
                Job.description.ilike(search_pattern)
            )
        )
    
    # Count total - use a simpler approach to avoid nested queries
    count_query = select(func.count(Job.id)).where(Job.is_active == True)

    if organization:
        count_query = count_query.where(Job.organization == organization)

    if category:
        count_query = count_query.where(Job.category == category)

    if grade:
        count_query = count_query.where(Job.grade == grade)

    if location:
        count_query = count_query.where(Job.location.ilike(f"%{location}%"))

    if keywords:
        search_pattern = f"%{keywords}%"
        count_query = count_query.where(
            or_(
                Job.title.ilike(search_pattern),
                Job.description.ilike(search_pattern)
            )
        )

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Job.created_at.desc())

    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return {
        "jobs": [JobResponse.model_validate(job) for job in jobs],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Get job details by ID."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse.model_validate(job)


@router.get("/filters/options", response_model=dict)
async def get_filter_options(db: AsyncSession = Depends(get_db)):
    """Get available filter options."""
    # Get unique values for each filter field
    organizations_result = await db.execute(
        select(Job.organization).distinct().where(Job.is_active == True)
    )
    organizations = [row[0] for row in organizations_result.all() if row[0]]
    
    categories_result = await db.execute(
        select(Job.category).distinct().where(Job.is_active == True)
    )
    categories = [row[0] for row in categories_result.all() if row[0]]
    
    grades_result = await db.execute(
        select(Job.grade).distinct().where(Job.is_active == True)
    )
    grades = [row[0] for row in grades_result.all() if row[0]]
    
    locations_result = await db.execute(
        select(Job.location).distinct().where(Job.is_active == True)
    )
    locations = [row[0] for row in locations_result.all() if row[0]]
    
    return {
        "organizations": sorted(organizations),
        "categories": sorted(categories),
        "grades": sorted(grades),
        "locations": sorted(locations)
    }



