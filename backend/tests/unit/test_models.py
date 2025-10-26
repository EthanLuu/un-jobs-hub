"""Tests for database models."""
import pytest
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from models.user import User
from models.job import Job
from models.resume import Resume
from models.favorite import Favorite
from utils.auth import get_password_hash


@pytest.mark.model
class TestUserModel:
    """Test User model."""
    
    async def test_create_user(self, db_session):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            full_name="Test User"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.created_at is not None
        assert user.is_active is True
    
    async def test_user_unique_email(self, db_session):
        """Test that email must be unique."""
        user1 = User(
            email="test@example.com",
            username="user1",
            hashed_password=get_password_hash("password123"),
            full_name="User 1"
        )
        
        user2 = User(
            email="test@example.com",  # Same email
            username="user2",
            hashed_password=get_password_hash("password123"),
            full_name="User 2"
        )
        
        db_session.add(user1)
        await db_session.commit()
        
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    async def test_user_unique_username(self, db_session):
        """Test that username must be unique."""
        user1 = User(
            email="user1@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            full_name="User 1"
        )
        
        user2 = User(
            email="user2@example.com",
            username="testuser",  # Same username
            hashed_password=get_password_hash("password123"),
            full_name="User 2"
        )
        
        db_session.add(user1)
        await db_session.commit()
        
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()


@pytest.mark.model
class TestJobModel:
    """Test Job model."""
    
    async def test_create_job(self, db_session):
        """Test creating a job."""
        job = Job(
            title="Software Engineer",
            organization="UN",
            job_id="UN-001",
            description="Test job description",
            location="Geneva",
            grade="P-3",
            contract_type="Fixed-term",
            category="Information Technology",
            education_level="Master's",
            years_of_experience=5,
            apply_url="https://example.com/apply",
            deadline=date(2025, 12, 31),
            posted_date=date.today(),
            source_url="https://example.com/job",
            is_active=True
        )
        
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)
        
        assert job.id is not None
        assert job.title == "Software Engineer"
        assert job.organization == "UN"
        assert job.job_id == "UN-001"
        assert job.location == "Geneva"
        assert job.grade == "P-3"
        assert job.is_active is True
        assert job.created_at is not None
    
    async def test_job_unique_job_id(self, db_session):
        """Test that job_id must be unique."""
        job1 = Job(
            title="Job 1",
            organization="UN",
            job_id="UN-001",
            description="Description 1",
            location="Geneva",
            grade="P-3",
            contract_type="Fixed-term",
            category="IT",
            apply_url="https://example.com/1",
            deadline=date(2025, 12, 31),
            posted_date=date.today(),
            source_url="https://example.com/job1",
            is_active=True
        )
        
        job2 = Job(
            title="Job 2",
            organization="UNDP",
            job_id="UN-001",  # Same job_id
            description="Description 2",
            location="New York",
            grade="P-4",
            contract_type="Temporary",
            category="Management",
            apply_url="https://example.com/2",
            deadline=date(2025, 11, 30),
            posted_date=date.today(),
            source_url="https://example.com/job2",
            is_active=True
        )
        
        db_session.add(job1)
        await db_session.commit()
        
        db_session.add(job2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()


@pytest.mark.model
class TestResumeModel:
    """Test Resume model."""
    
    async def test_create_resume(self, db_session, test_user):
        """Test creating a resume."""
        resume = Resume(
            user_id=test_user.id,
            filename="test_resume.pdf",
            raw_text="Test resume content",
            skills=["Python", "JavaScript", "Leadership"],
            experience_years=5,
            education_level="Master's",
            is_active=True
        )
        
        db_session.add(resume)
        await db_session.commit()
        await db_session.refresh(resume)
        
        assert resume.id is not None
        assert resume.user_id == test_user.id
        assert resume.filename == "test_resume.pdf"
        assert resume.raw_text == "Test resume content"
        assert resume.skills == ["Python", "JavaScript", "Leadership"]
        assert resume.experience_years == 5
        assert resume.education_level == "Master's"
        assert resume.is_active is True
        assert resume.created_at is not None
    
    async def test_resume_user_relationship(self, db_session, test_user):
        """Test resume-user relationship."""
        resume = Resume(
            user_id=test_user.id,
            filename="test_resume.pdf",
            raw_text="Test resume content",
            skills=["Python"],
            experience_years=3,
            education_level="Bachelor's",
            is_active=True
        )
        
        db_session.add(resume)
        await db_session.commit()
        await db_session.refresh(resume)
        
        # Test relationship
        assert resume.user == test_user
        assert resume in test_user.resumes


@pytest.mark.model
class TestFavoriteModel:
    """Test Favorite model."""
    
    async def test_create_favorite(self, db_session, test_user, test_job):
        """Test creating a favorite."""
        favorite = Favorite(
            user_id=test_user.id,
            job_id=test_job.id,
            status="interested",
            notes="This looks interesting"
        )
        
        db_session.add(favorite)
        await db_session.commit()
        await db_session.refresh(favorite)
        
        assert favorite.id is not None
        assert favorite.user_id == test_user.id
        assert favorite.job_id == test_job.id
        assert favorite.status == "interested"
        assert favorite.notes == "This looks interesting"
        assert favorite.created_at is not None
    
    async def test_favorite_unique_user_job(self, db_session, test_user, test_job):
        """Test that user can only favorite a job once."""
        favorite1 = Favorite(
            user_id=test_user.id,
            job_id=test_job.id,
            status="interested"
        )
        
        favorite2 = Favorite(
            user_id=test_user.id,
            job_id=test_job.id,  # Same user and job
            status="applied"
        )
        
        db_session.add(favorite1)
        await db_session.commit()
        
        db_session.add(favorite2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    async def test_favorite_relationships(self, db_session, test_user, test_job):
        """Test favorite relationships."""
        favorite = Favorite(
            user_id=test_user.id,
            job_id=test_job.id,
            status="interested"
        )
        
        db_session.add(favorite)
        await db_session.commit()
        await db_session.refresh(favorite)
        
        # Test relationships
        assert favorite.user == test_user
        assert favorite.job == test_job
        assert favorite in test_user.favorites
        assert favorite in test_job.favorites
