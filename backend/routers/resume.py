"""Resume management routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import uuid
from pathlib import Path

from database import get_db
from models.user import User
from models.resume import Resume
from schemas.resume import ResumeResponse
from utils.auth import get_current_user
from services.resume_parser import parse_resume
from config import settings

router = APIRouter()


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's resumes."""
    result = await db.execute(
        select(Resume).where(Resume.user_id == current_user.id)
    )
    resumes = result.scalars().all()
    return [ResumeResponse.model_validate(resume) for resume in resumes]


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse a resume."""
    # Validate file type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed"
        )
    
    # Validate file size
    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.max_file_size} bytes"
        )
    
    # Save file
    upload_dir = Path(settings.upload_dir) / "resumes"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Parse resume
    try:
        parsed_data = await parse_resume(str(file_path), file.content_type)
    except Exception as e:
        # Clean up file if parsing fails
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume: {str(e)}"
        )
    
    # Deactivate previous resumes
    await db.execute(
        select(Resume).where(Resume.user_id == current_user.id)
    )
    prev_resumes = (await db.execute(
        select(Resume).where(Resume.user_id == current_user.id)
    )).scalars().all()
    
    for prev_resume in prev_resumes:
        prev_resume.is_active = False
    
    # Create resume record
    new_resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(file_path),
        file_type=file_ext.lstrip('.'),
        raw_text=parsed_data.get("raw_text", ""),
        parsed_data=parsed_data.get("structured_data"),
        skills=parsed_data.get("skills"),
        experience_years=parsed_data.get("experience_years")
    )
    
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)
    
    return ResumeResponse.model_validate(new_resume)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get resume details."""
    result = await db.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return ResumeResponse.model_validate(resume)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a resume."""
    result = await db.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file
    file_path = resume.file_path
    
    await db.delete(resume)
    await db.commit()
    
    # Delete file after database commit
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return None



