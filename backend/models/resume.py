"""Resume model."""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Resume(Base):
    """User's resume/CV for job matching."""
    
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File info
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)  # pdf, docx
    
    # Parsed content
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSON, nullable=True)  # Structured data
    
    # AI Analysis
    embedding = Column(JSON, nullable=True)  # Vector embedding
    skills = Column(JSON, nullable=True)  # Extracted skills
    experience_years = Column(Integer, nullable=True)
    education = Column(JSON, nullable=True)
    
    # Status
    is_active = Column(String, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resumes")



