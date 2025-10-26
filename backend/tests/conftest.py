"""Test configuration and fixtures."""
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from faker import Faker
from typing import AsyncGenerator, Generator
import os
import tempfile
from pathlib import Path

from database import get_async_session, Base
from main import app
from models.user import User
from models.job import Job
from models.resume import Resume
from models.favorite import Favorite
from utils.auth import get_password_hash, create_access_token

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

fake = Faker()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create test database."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(test_db) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session = sessionmaker(
        test_db, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_async_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """Generate test user data."""
    return {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": "testpassword123",
        "full_name": fake.name()
    }

@pytest_asyncio.fixture
async def test_user(db_session, test_user_data) -> User:
    """Create test user."""
    user = User(
        email=test_user_data["email"],
        username=test_user_data["username"],
        hashed_password=get_password_hash(test_user_data["password"]),
        full_name=test_user_data["full_name"]
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers."""
    token = create_access_token(data={"user_id": test_user.id, "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_job_data():
    """Generate test job data."""
    return {
        "title": fake.job(),
        "organization": fake.random_element(elements=("UN", "UNDP", "UNICEF", "WHO", "FAO")),
        "job_id": fake.uuid4(),
        "description": fake.text(max_nb_chars=500),
        "location": fake.city(),
        "grade": fake.random_element(elements=("P-1", "P-2", "P-3", "P-4", "P-5")),
        "contract_type": fake.random_element(elements=("Fixed-term", "Temporary", "Consultant")),
        "category": fake.random_element(elements=("Programme Management", "Information Technology", "Administration")),
        "education_level": fake.random_element(elements=("Bachelor's", "Master's", "PhD")),
        "years_of_experience": fake.random_int(min=1, max=10),
        "apply_url": fake.url(),
        "deadline": fake.future_date(),
        "posted_date": fake.past_date(),
        "source_url": fake.url(),
        "is_active": True
    }

@pytest_asyncio.fixture
async def test_job(db_session, test_job_data) -> Job:
    """Create test job."""
    job = Job(**test_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    return job

@pytest.fixture
def test_resume_data(test_user):
    """Generate test resume data."""
    return {
        "user_id": test_user.id,
        "filename": "test_resume.pdf",
        "raw_text": fake.text(max_nb_chars=1000),
        "skills": ["Python", "JavaScript", "Project Management", "Leadership"],
        "experience_years": fake.random_int(min=1, max=15),
        "education_level": "Master's",
        "is_active": True
    }

@pytest_asyncio.fixture
async def test_resume(db_session, test_resume_data) -> Resume:
    """Create test resume."""
    resume = Resume(**test_resume_data)
    db_session.add(resume)
    await db_session.commit()
    await db_session.refresh(resume)
    return resume

@pytest.fixture
def temp_file():
    """Create temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Test file content")
        tmp_path = tmp.name
    
    yield tmp_path
    
    # Clean up
    os.unlink(tmp_path)

@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls."""
    class MockOpenAI:
        class ChatCompletion:
            def __init__(self, content="Test recommendation"):
                self.message = type('Message', (), {'content': content})()
                self.choices = [self]
        
        async def chat_completions_create(self, **kwargs):
            return self.ChatCompletion()
    
    return MockOpenAI()

# Test markers
pytestmark = pytest.mark.asyncio
