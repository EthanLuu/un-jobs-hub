"""Favorite/bookmark model."""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Favorite(Base):
    """User's favorite/bookmarked jobs."""
    
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # User notes
    notes = Column(Text, nullable=True)
    status = Column(String, default="saved")  # saved, applied, interview, rejected
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    job = relationship("Job", back_populates="favorites")



