"""Job listing routes."""
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, distinct
from typing import List, Optional

from database import get_db
from models.job import Job
from models.user import User
from schemas.job import JobResponse, JobFilter
from utils.auth import get_current_user

router = APIRouter()


def build_filter_conditions(
    organization: Optional[str] = None,
    category: Optional[str] = None,
    grade: Optional[str] = None,
    location: Optional[str] = None,
    education_level: Optional[str] = None,
    min_experience: Optional[int] = None,
    max_experience: Optional[int] = None,
    remote_eligible: Optional[bool] = None,
    keywords: Optional[str] = None,
    contract_types: Optional[List[str]] = None,
    exclude_contract_types: Optional[List[str]] = None,
):
    """Build filter conditions for job queries."""
    conditions = [Job.is_active == True]
    
    if organization:
        conditions.append(Job.organization == organization)
    
    if category:
        conditions.append(Job.category == category)
    
    if grade:
        conditions.append(Job.grade == grade)
    
    if location:
        # Optimize ILIKE: use prefix pattern when possible
        if location and not location.startswith('%'):
            # Can use index if it's a prefix search
            conditions.append(Job.location.ilike(f"{location}%"))
        else:
            conditions.append(Job.location.ilike(f"%{location}%"))
    
    if education_level:
        conditions.append(Job.education_level == education_level)
    
    if min_experience is not None:
        conditions.append(Job.years_of_experience >= min_experience)
    
    if max_experience is not None:
        conditions.append(Job.years_of_experience <= max_experience)
    
    if remote_eligible is not None:
        if remote_eligible:
            conditions.append(Job.remote_eligible.ilike("%yes%"))
        else:
            conditions.append(Job.remote_eligible.ilike("%no%"))
    
    if keywords:
        search_pattern = f"%{keywords}%"
        # Use OR conditions for keyword search across multiple fields
        conditions.append(
            or_(
                Job.title.ilike(search_pattern),
                Job.description.ilike(search_pattern),
                Job.responsibilities.ilike(search_pattern),
                Job.qualifications.ilike(search_pattern),
                Job.organization.ilike(search_pattern)
            )
        )
    
    # Multi-select contract types
    if contract_types and len(contract_types) > 0:
        conditions.append(Job.contract_type.in_(contract_types))
    
    # Exclude contract types
    if exclude_contract_types and len(exclude_contract_types) > 0:
        conditions.append(~Job.contract_type.in_(exclude_contract_types))
    
    return conditions


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
    contract_types: Optional[List[str]] = Query(None),
    exclude_contract_types: Optional[List[str]] = Query(None),
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
    # Build filter conditions once
    filter_conditions = build_filter_conditions(
        organization=organization,
        category=category,
        grade=grade,
        location=location,
        education_level=education_level,
        min_experience=min_experience,
        max_experience=max_experience,
        remote_eligible=remote_eligible,
        keywords=keywords,
        contract_types=contract_types,
        exclude_contract_types=exclude_contract_types
    )
    
    # Count query - use the same filter conditions
    count_query = select(func.count(Job.id)).where(*filter_conditions)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Main query
    query = select(Job).where(*filter_conditions)
    
    # Sorting
    sort_column = getattr(Job, sort_by)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)

    # Execute query
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
    # Build base query for active jobs only
    base_query = select(Job).where(Job.is_active == True)
    
    # Get unique values for each filter field
    # Using distinct() with .all() for better performance
    organizations_result = await db.execute(
        select(distinct(Job.organization))
        .where(Job.is_active == True)
        .where(Job.organization.isnot(None))
        .order_by(Job.organization)
    )
    organizations = [row[0] for row in organizations_result.all()]

    categories_result = await db.execute(
        select(distinct(Job.category))
        .where(Job.is_active == True)
        .where(Job.category.isnot(None))
        .order_by(Job.category)
    )
    categories = [row[0] for row in categories_result.all()]

    grades_result = await db.execute(
        select(distinct(Job.grade))
        .where(Job.is_active == True)
        .where(Job.grade.isnot(None))
        .where(Job.grade.notilike('%day%'))
        .where(Job.grade.notilike('%monday%'))
        .where(Job.grade.notilike('%tuesday%'))
        .where(Job.grade.notilike('%wednesday%'))
        .where(Job.grade.notilike('%thursday%'))
        .where(Job.grade.notilike('%friday%'))
        .where(Job.grade.notilike('%saturday%'))
        .where(Job.grade.notilike('%sunday%'))
        .where(Job.grade.notilike('%november%'))
        .where(Job.grade.notilike('%october%'))
        .where(Job.grade.notilike('%december%'))
        .where(Job.grade.notilike('%january%'))
        .order_by(Job.grade)
    )
    grades = [row[0] for row in grades_result.all()]
    
    # Filter out dates and invalid grades
    grades = [
        grade for grade in grades 
        if re.match(r'^[A-Z0-9-]+$', grade) and len(grade) <= 20
    ]

    locations_result = await db.execute(
        select(distinct(Job.location))
        .where(Job.is_active == True)
        .where(Job.location.isnot(None))
        .order_by(Job.location)
    )
    locations = [row[0] for row in locations_result.all()]

    education_levels_result = await db.execute(
        select(distinct(Job.education_level))
        .where(Job.is_active == True)
        .where(Job.education_level.isnot(None))
        .order_by(Job.education_level)
    )
    education_levels = [row[0] for row in education_levels_result.all()]

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



