"""Base crawler class with enhanced error handling and monitoring."""
from typing import List, Dict, Optional, Callable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from config import settings
from models.job import Job
import logging
import time
import traceback
from enum import Enum


class CrawlerStatus(Enum):
    """Crawler status enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"


class CrawlerMetrics:
    """Crawler metrics collection."""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.jobs_found: int = 0
        self.jobs_saved: int = 0
        self.jobs_updated: int = 0
        self.jobs_failed: int = 0
        self.errors: List[str] = []
        self.status: CrawlerStatus = CrawlerStatus.IDLE
        self.retry_count: int = 0

    @property
    def duration_seconds(self) -> float:
        """Get crawl duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    @property
    def success_rate(self) -> float:
        """Get success rate percentage."""
        total = self.jobs_found
        if total == 0:
            return 0.0
        successful = self.jobs_saved + self.jobs_updated
        return (successful / total) * 100

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "jobs_found": self.jobs_found,
            "jobs_saved": self.jobs_saved,
            "jobs_updated": self.jobs_updated,
            "jobs_failed": self.jobs_failed,
            "success_rate": self.success_rate,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "errors": self.errors[:10]  # Limit to last 10 errors
        }


class BaseCrawler:
    """Base class for all job crawlers with enhanced error handling."""

    def __init__(
        self,
        organization: str,
        max_retries: int = 3,
        retry_delay: int = 5,
        timeout: int = 300
    ):
        """
        Initialize base crawler.

        Args:
            organization: Organization name
            max_retries: Maximum number of retries on failure
            retry_delay: Delay between retries in seconds
            timeout: Maximum crawl time in seconds
        """
        self.organization = organization
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.metrics = CrawlerMetrics()
        self.logger = logging.getLogger(f"{__name__}.{organization}")

        # Create synchronous engine for use in Celery tasks
        # Replace async drivers with sync equivalents
        db_url = settings.database_url
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        db_url = db_url.replace("postgresql+psycopg://", "postgresql://")
        db_url = db_url.replace("sqlite+aiosqlite:///", "sqlite:///")
        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _retry_with_backoff(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Optional[any]:
        """
        Retry function with exponential backoff.

        Args:
            func: Function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result or None on failure
        """
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.metrics.retry_count += 1
                delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                error_msg = f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}"
                self.logger.warning(error_msg)
                self.metrics.errors.append(error_msg)

                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"All retry attempts exhausted for {func.__name__}")
                    raise
        return None

    def save_jobs(self, jobs_data: List[Dict]) -> Dict[str, int]:
        """
        Save crawled jobs to database with error handling.

        Args:
            jobs_data: List of job dictionaries

        Returns:
            Dictionary with saved and updated counts
        """
        if not jobs_data:
            self.logger.warning("No jobs data to save")
            return {"saved": 0, "updated": 0, "failed": 0}

        session = self.SessionLocal()
        saved_count = 0
        updated_count = 0
        failed_count = 0

        try:
            for job_data in jobs_data:
                try:
                    # Validate required fields
                    if not job_data.get("job_id"):
                        self.logger.error(f"Missing job_id for job: {job_data.get('title', 'Unknown')}")
                        failed_count += 1
                        continue

                    # Check if job already exists
                    existing_job = session.query(Job).filter(
                        Job.job_id == job_data["job_id"]
                    ).first()

                    if existing_job:
                        # Update existing job
                        for key, value in job_data.items():
                            if hasattr(existing_job, key):
                                setattr(existing_job, key, value)
                        existing_job.last_scraped = datetime.utcnow()
                        updated_count += 1
                        self.logger.debug(f"Updated: {job_data.get('title', 'Unknown')}")
                    else:
                        # Create new job
                        new_job = Job(**job_data)
                        session.add(new_job)
                        saved_count += 1
                        self.logger.info(f"Added: {job_data.get('title', 'Unknown')}")

                    # Commit in batches of 10 for better performance
                    if (saved_count + updated_count) % 10 == 0:
                        session.commit()

                except Exception as e:
                    failed_count += 1
                    error_msg = f"Failed to save job {job_data.get('title', 'Unknown')}: {str(e)}"
                    self.logger.error(error_msg)
                    self.metrics.errors.append(error_msg)
                    session.rollback()

            # Final commit
            session.commit()

            self.logger.info(
                f"Save results: {saved_count} new, {updated_count} updated, {failed_count} failed"
            )

            # Update metrics
            self.metrics.jobs_saved = saved_count
            self.metrics.jobs_updated = updated_count
            self.metrics.jobs_failed = failed_count

            return {
                "saved": saved_count,
                "updated": updated_count,
                "failed": failed_count
            }

        except Exception as e:
            session.rollback()
            error_msg = f"Database error while saving jobs: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            self.metrics.errors.append(error_msg)
            raise
        finally:
            session.close()

    def crawl(self) -> Dict:
        """Override this method in subclasses."""
        raise NotImplementedError("Subclasses must implement crawl() method")

    def run(self) -> Dict:
        """
        Run the crawler with error handling and metrics collection.

        Returns:
            Dictionary with crawl results and metrics
        """
        self.metrics = CrawlerMetrics()  # Reset metrics
        self.metrics.start_time = time.time()
        self.metrics.status = CrawlerStatus.RUNNING

        self.logger.info(f"Starting crawl for {self.organization}")

        try:
            # Run crawl with timeout
            result = self._retry_with_backoff(self.crawl)

            if result:
                self.metrics.jobs_found = len(result.get("jobs", []))

                if self.metrics.jobs_found > 0:
                    # Save jobs to database
                    save_result = self.save_jobs(result.get("jobs", []))

                    # Determine final status
                    if save_result["failed"] == 0:
                        self.metrics.status = CrawlerStatus.SUCCESS
                    else:
                        self.metrics.status = CrawlerStatus.PARTIAL_SUCCESS
                else:
                    self.metrics.status = CrawlerStatus.SUCCESS
                    self.logger.warning("No jobs found during crawl")
            else:
                self.metrics.status = CrawlerStatus.FAILED
                self.logger.error("Crawl returned no results")

        except Exception as e:
            self.metrics.status = CrawlerStatus.FAILED
            error_msg = f"Crawl failed with error: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            self.metrics.errors.append(error_msg)

        finally:
            self.metrics.end_time = time.time()
            duration = self.metrics.duration_seconds

            self.logger.info(
                f"Crawl completed in {duration:.2f}s - "
                f"Status: {self.metrics.status.value}, "
                f"Jobs: {self.metrics.jobs_found} found, "
                f"{self.metrics.jobs_saved} saved, "
                f"{self.metrics.jobs_updated} updated, "
                f"{self.metrics.jobs_failed} failed"
            )

        return self.metrics.to_dict()



