"""Resume schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List


class ResumeUpload(BaseModel):
    """Schema for resume upload response."""
    filename: str
    file_type: str


class ResumeResponse(BaseModel):
    """Schema for resume response."""
    id: int
    user_id: int
    filename: str
    file_type: str
    skills: Optional[List[str]]
    experience_years: Optional[int]
    education_level: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeAnalysis(BaseModel):
    """Schema for resume analysis result."""
    skills: List[str]
    experience_years: int
    education: List[Dict]
    key_achievements: List[str]



