"""Favorite schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FavoriteCreate(BaseModel):
    """Schema for creating a favorite."""
    job_id: int
    notes: Optional[str] = None


class FavoriteUpdate(BaseModel):
    """Schema for updating a favorite."""
    notes: Optional[str] = None
    status: Optional[str] = None  # saved, applied, interview, rejected


class FavoriteResponse(BaseModel):
    """Schema for favorite response."""
    id: int
    user_id: int
    job_id: int
    notes: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True



