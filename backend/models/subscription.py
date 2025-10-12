"""Subscription model for job alerts."""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Subscription(Base):
    """User's job alert subscriptions."""
    
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Subscription settings
    name = Column(String, nullable=False)  # e.g., "Programme Jobs in Asia"
    
    # Filters
    filters = Column(JSON, nullable=False)  # {organization: [...], category: [...], location: [...]}
    
    # Notification settings
    notification_type = Column(String, default="email")  # email, wechat
    frequency = Column(String, default="daily")  # daily, weekly, instant
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sent = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")



