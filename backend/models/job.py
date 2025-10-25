"""Job posting model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Job(Base):
    """Job posting model for UN system positions."""
    
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    title = Column(String, nullable=False, index=True)
    organization = Column(String, nullable=False, index=True)  # UNDP, UNICEF, WHO, etc.
    job_id = Column(String, unique=True, index=True)  # Original job ID from source
    
    # Details
    description = Column(Text, nullable=False)
    responsibilities = Column(Text, nullable=True)
    qualifications = Column(Text, nullable=True)
    
    # Classification
    category = Column(String, index=True)  # Programme Management, Finance, etc.
    grade = Column(String, index=True)  # P-3, P-4, G-5, etc.
    contract_type = Column(String, index=True)  # Fixed-term, Temporary, Consultant
    
    # Location
    location = Column(String, index=True)
    duty_station = Column(String)
    remote_eligible = Column(String, default="No")
    
    # Requirements
    language_requirements = Column(JSON)  # {en: required, fr: desirable}
    education_level = Column(String, index=True)
    years_of_experience = Column(Integer, index=True)
    
    # Application
    apply_url = Column(String, nullable=False)
    deadline = Column(Date, index=True)
    posted_date = Column(Date)
    
    # Metadata
    source_url = Column(String)
    embedding = Column(JSON, nullable=True)  # Vector embedding for matching
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_scraped = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    favorites = relationship("Favorite", back_populates="job", cascade="all, delete-orphan")



