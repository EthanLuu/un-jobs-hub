"""Job schemas."""
from pydantic import BaseModel, HttpUrl
from datetime import date, datetime
from typing import Optional, Dict, List


class JobCreate(BaseModel):
    """Schema for creating a job."""
    title: str
    organization: str
    job_id: str
    description: str
    responsibilities: Optional[str] = None
    qualifications: Optional[str] = None
    category: Optional[str] = None
    grade: Optional[str] = None
    contract_type: Optional[str] = None
    location: Optional[str] = None
    duty_station: Optional[str] = None
    remote_eligible: str = "No"
    language_requirements: Optional[Dict] = None
    education_level: Optional[str] = None
    years_of_experience: Optional[int] = None
    apply_url: str
    deadline: Optional[date] = None
    posted_date: Optional[date] = None
    source_url: Optional[str] = None


class JobResponse(BaseModel):
    """Schema for job response."""
    id: int
    title: str
    organization: str
    job_id: str
    description: str
    responsibilities: Optional[str] = None
    qualifications: Optional[str] = None
    category: Optional[str]
    grade: Optional[str]
    contract_type: Optional[str]
    location: Optional[str]
    duty_station: Optional[str]
    remote_eligible: str
    language_requirements: Optional[Dict]
    education_level: Optional[str] = None
    years_of_experience: Optional[int] = None
    apply_url: str
    deadline: Optional[date]
    posted_date: Optional[date]
    source_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_scraped: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobFilter(BaseModel):
    """Schema for filtering jobs."""
    organization: Optional[List[str]] = None
    category: Optional[List[str]] = None
    grade: Optional[List[str]] = None
    location: Optional[List[str]] = None
    contract_type: Optional[str] = None
    remote_eligible: Optional[bool] = None
    keywords: Optional[str] = None
    page: int = 1
    page_size: int = 20



