"""Base crawler class."""
from typing import List, Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings
from models.job import Job


class BaseCrawler:
    """Base class for all job crawlers."""
    
    def __init__(self, organization: str):
        self.organization = organization
        # Create synchronous engine for use in Celery tasks
        # Replace async drivers with sync equivalents
        db_url = settings.database_url
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        db_url = db_url.replace("sqlite+aiosqlite:///", "sqlite:///")
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def save_jobs(self, jobs_data: List[Dict]) -> int:
        """Save crawled jobs to database."""
        session = self.SessionLocal()
        saved_count = 0
        
        try:
            for job_data in jobs_data:
                # Check if job already exists
                existing_job = session.query(Job).filter(
                    Job.job_id == job_data["job_id"]
                ).first()
                
                if existing_job:
                    # Update existing job
                    for key, value in job_data.items():
                        setattr(existing_job, key, value)
                    existing_job.last_scraped = datetime.utcnow()
                else:
                    # Create new job
                    new_job = Job(**job_data)
                    session.add(new_job)
                    saved_count += 1
            
            session.commit()
            return saved_count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def crawl(self) -> Dict:
        """Override this method in subclasses."""
        raise NotImplementedError("Subclasses must implement crawl() method")



