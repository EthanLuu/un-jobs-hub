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
    education_level: Optional[str] = None,
    min_experience: Optional[int] = None,
    max_experience: Optional[int] = None,
    remote_eligible: Optional[bool] = None,
    keywords: Optional[str] = None,
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|deadline|posted_date|title)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """List jobs with filtering, sorting and pagination.

    Search fields:
    - keywords: Search in title, description, responsibilities, qualifications
    - organization: Exact match
    - category: Exact match
    - grade: Exact match
    - location: Partial match (case-insensitive)
    - education_level: Exact match
    - min_experience/max_experience: Range filter
    - remote_eligible: Boolean filter

    Sorting:
    - sort_by: created_at (default), deadline, posted_date, title
    - sort_order: desc (default), asc
    """
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

    if education_level:
        query = query.where(Job.education_level == education_level)

    if min_experience is not None:
        query = query.where(Job.years_of_experience >= min_experience)

    if max_experience is not None:
        query = query.where(Job.years_of_experience <= max_experience)

    if remote_eligible is not None:
        if remote_eligible:
            query = query.where(Job.remote_eligible.ilike("%yes%"))
        else:
            query = query.where(Job.remote_eligible.ilike("%no%"))

    if keywords:
        search_pattern = f"%{keywords}%"
        query = query.where(
            or_(
                Job.title.ilike(search_pattern),
                Job.description.ilike(search_pattern),
                Job.responsibilities.ilike(search_pattern),
                Job.qualifications.ilike(search_pattern),
                Job.organization.ilike(search_pattern)
            )
        )

    # Count total
    count_query = select(func.count(Job.id)).where(Job.is_active == True)

    if organization:
        count_query = count_query.where(Job.organization == organization)

    if category:
        count_query = count_query.where(Job.category == category)

    if grade:
        count_query = count_query.where(Job.grade == grade)

    if location:
        count_query = count_query.where(Job.location.ilike(f"%{location}%"))

    if education_level:
        count_query = count_query.where(Job.education_level == education_level)

    if min_experience is not None:
        count_query = count_query.where(Job.years_of_experience >= min_experience)

    if max_experience is not None:
        count_query = count_query.where(Job.years_of_experience <= max_experience)

    if remote_eligible is not None:
        if remote_eligible:
            count_query = count_query.where(Job.remote_eligible.ilike("%yes%"))
        else:
            count_query = count_query.where(Job.remote_eligible.ilike("%no%"))

    if keywords:
        search_pattern = f"%{keywords}%"
        count_query = count_query.where(
            or_(
                Job.title.ilike(search_pattern),
                Job.description.ilike(search_pattern),
                Job.responsibilities.ilike(search_pattern),
                Job.qualifications.ilike(search_pattern),
                Job.organization.ilike(search_pattern)
            )
        )

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Sorting
    sort_column = getattr(Job, sort_by)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)

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
        select(Job.organization).distinct().where(Job.is_active == True).order_by(Job.organization)
    )
    organizations = [row[0] for row in organizations_result.all() if row[0]]

    categories_result = await db.execute(
        select(Job.category).distinct().where(Job.is_active == True).order_by(Job.category)
    )
    categories = [row[0] for row in categories_result.all() if row[0]]

    grades_result = await db.execute(
        select(Job.grade).distinct().where(Job.is_active == True).order_by(Job.grade)
    )
    grades = [row[0] for row in grades_result.all() if row[0]]

    locations_result = await db.execute(
        select(Job.location).distinct().where(Job.is_active == True).order_by(Job.location)
    )
    locations = [row[0] for row in locations_result.all() if row[0]]

    education_levels_result = await db.execute(
        select(Job.education_level).distinct().where(Job.is_active == True).order_by(Job.education_level)
    )
    education_levels = [row[0] for row in education_levels_result.all() if row[0]]

    # Get experience range
    experience_result = await db.execute(
        select(
            func.min(Job.years_of_experience),
            func.max(Job.years_of_experience)
        ).where(Job.is_active == True, Job.years_of_experience.isnot(None))
    )
    exp_min, exp_max = experience_result.first()

    return {
        "organizations": organizations,
        "categories": categories,
        "grades": grades,
        "locations": locations,
        "education_levels": education_levels,
        "experience_range": {
            "min": exp_min or 0,
            "max": exp_max or 20
        }
    }



