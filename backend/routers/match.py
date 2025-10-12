"""Job matching routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models.user import User
from models.job import Job
from models.resume import Resume
from schemas.match import MatchRequest, MatchResponse, MatchResult
from utils.auth import get_current_user
from services.matching_service import calculate_match_score

router = APIRouter()


@router.post("/", response_model=MatchResult)
async def match_resume_to_jobs(
    match_request: MatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Match a resume to jobs."""
    # Get resume
    resume_result = await db.execute(
        select(Resume).where(
            Resume.id == match_request.resume_id,
            Resume.user_id == current_user.id
        )
    )
    resume = resume_result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get jobs to match against
    if match_request.job_id:
        # Match against specific job
        job_result = await db.execute(
            select(Job).where(Job.id == match_request.job_id)
        )
        jobs = [job_result.scalar_one_or_none()]
        if not jobs[0]:
            raise HTTPException(status_code=404, detail="Job not found")
    else:
        # Match against all active jobs
        jobs_result = await db.execute(
            select(Job).where(Job.is_active == True).limit(50)
        )
        jobs = jobs_result.scalars().all()
    
    # Calculate matches
    matches = []
    for job in jobs:
        match_result = await calculate_match_score(resume, job)
        matches.append(MatchResponse(
            job_id=job.id,
            match_score=match_result["score"],
            missing_keywords=match_result["missing_keywords"],
            matching_keywords=match_result["matching_keywords"],
            recommendation=match_result["recommendation"]
        ))
    
    # Sort by match score
    matches.sort(key=lambda x: x.match_score, reverse=True)
    
    return MatchResult(
        matches=matches[:20],  # Return top 20 matches
        resume_id=resume.id
    )


@router.get("/job/{job_id}", response_model=MatchResponse)
async def match_current_resume_to_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Match user's active resume to a specific job."""
    # Get active resume
    resume_result = await db.execute(
        select(Resume).where(
            Resume.user_id == current_user.id,
            Resume.is_active == True
        )
    )
    resume = resume_result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=404,
            detail="No active resume found. Please upload a resume first."
        )
    
    # Get job
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Calculate match
    match_result = await calculate_match_score(resume, job)
    
    return MatchResponse(
        job_id=job.id,
        match_score=match_result["score"],
        missing_keywords=match_result["missing_keywords"],
        matching_keywords=match_result["matching_keywords"],
        recommendation=match_result["recommendation"]
    )



