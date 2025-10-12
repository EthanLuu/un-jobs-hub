"""Matching schemas."""
from pydantic import BaseModel
from typing import List, Optional


class MatchRequest(BaseModel):
    """Schema for job matching request."""
    resume_id: int
    job_id: Optional[int] = None  # If None, match against all jobs


class MatchResponse(BaseModel):
    """Schema for job matching response."""
    job_id: int
    match_score: float
    missing_keywords: List[str]
    matching_keywords: List[str]
    recommendation: str
    
    class Config:
        from_attributes = True


class MatchResult(BaseModel):
    """Schema for multiple match results."""
    matches: List[MatchResponse]
    resume_id: int



