"""Tests for API endpoints."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import json


@pytest.mark.api
class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["username"] == user_data["username"]
        assert data["user"]["full_name"] == user_data["full_name"]
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with duplicate email."""
        user_data = {
            "email": test_user.email,  # Same email as existing user
            "username": "newuser",
            "password": "testpassword123",
            "full_name": "New User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Test registration with duplicate username."""
        user_data = {
            "email": "new@example.com",
            "username": test_user.username,  # Same username as existing user
            "password": "testpassword123",
            "full_name": "New User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]
    
    async def test_login_success(self, client: AsyncClient, test_user, test_user_data):
        """Test successful login."""
        login_data = {
            "email": test_user.email,
            "password": test_user_data["password"]
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_user.email
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    async def test_get_current_user(self, client: AsyncClient, auth_headers, test_user):
        """Test getting current user info."""
        response = await client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["full_name"] == test_user.full_name
    
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication."""
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 401


@pytest.mark.api
class TestJobEndpoints:
    """Test job endpoints."""
    
    async def test_list_jobs(self, client: AsyncClient, test_job):
        """Test listing jobs."""
        response = await client.get("/api/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert len(data["jobs"]) > 0
    
    async def test_list_jobs_with_filters(self, client: AsyncClient, test_job):
        """Test listing jobs with filters."""
        response = await client.get(f"/api/jobs?organization={test_job.organization}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) > 0
        
        # All returned jobs should match the filter
        for job in data["jobs"]:
            assert job["organization"] == test_job.organization
    
    async def test_list_jobs_pagination(self, client: AsyncClient):
        """Test job listing pagination."""
        response = await client.get("/api/jobs?page=1&page_size=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["jobs"]) <= 5
    
    async def test_get_job_by_id(self, client: AsyncClient, test_job):
        """Test getting job by ID."""
        response = await client.get(f"/api/jobs/{test_job.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_job.id
        assert data["title"] == test_job.title
        assert data["organization"] == test_job.organization
    
    async def test_get_job_not_found(self, client: AsyncClient):
        """Test getting non-existent job."""
        response = await client.get("/api/jobs/99999")
        
        assert response.status_code == 404
        assert "Job not found" in response.json()["detail"]
    
    async def test_get_job_filters_options(self, client: AsyncClient):
        """Test getting filter options."""
        response = await client.get("/api/jobs/filters/options")
        
        assert response.status_code == 200
        data = response.json()
        assert "organizations" in data
        assert "categories" in data
        assert "grades" in data
        assert "locations" in data
        assert "education_levels" in data


@pytest.mark.api
class TestResumeEndpoints:
    """Test resume endpoints."""
    
    async def test_list_resumes(self, client: AsyncClient, auth_headers, test_resume):
        """Test listing user's resumes."""
        response = await client.get("/api/resume/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["id"] == test_resume.id
        assert data[0]["filename"] == test_resume.filename
    
    async def test_list_resumes_unauthorized(self, client: AsyncClient):
        """Test listing resumes without authentication."""
        response = await client.get("/api/resume/")
        
        assert response.status_code == 401
    
    async def test_upload_resume(self, client: AsyncClient, auth_headers, temp_file):
        """Test resume upload."""
        with patch('services.resume_parser.parse_resume') as mock_parse:
            mock_parse.return_value = {
                "raw_text": "Test resume content",
                "skills": ["Python", "JavaScript"],
                "experience_years": 5,
                "education_level": "Master's"
            }
            
            with open(temp_file, "rb") as f:
                files = {"file": ("test_resume.pdf", f, "application/pdf")}
                response = await client.post("/api/resume/upload", files=files, headers=auth_headers)
            
            assert response.status_code == 201
            data = response.json()
            assert data["filename"] == "test_resume.pdf"
            assert data["skills"] == ["Python", "JavaScript"]
            assert data["experience_years"] == 5
    
    async def test_get_resume_by_id(self, client: AsyncClient, auth_headers, test_resume):
        """Test getting resume by ID."""
        response = await client.get(f"/api/resume/{test_resume.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_resume.id
        assert data["filename"] == test_resume.filename
    
    async def test_get_resume_not_found(self, client: AsyncClient, auth_headers):
        """Test getting non-existent resume."""
        response = await client.get("/api/resume/99999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "Resume not found" in response.json()["detail"]
    
    async def test_delete_resume(self, client: AsyncClient, auth_headers, test_resume):
        """Test deleting resume."""
        response = await client.delete(f"/api/resume/{test_resume.id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify resume is deleted
        response = await client.get(f"/api/resume/{test_resume.id}", headers=auth_headers)
        assert response.status_code == 404


@pytest.mark.api
class TestFavoriteEndpoints:
    """Test favorite endpoints."""
    
    async def test_list_favorites(self, client: AsyncClient, auth_headers):
        """Test listing user's favorites."""
        response = await client.get("/api/favorites", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_add_favorite(self, client: AsyncClient, auth_headers, test_job):
        """Test adding job to favorites."""
        favorite_data = {
            "job_id": test_job.id,
            "status": "interested",
            "notes": "This looks interesting"
        }
        
        response = await client.post("/api/favorites", json=favorite_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["job_id"] == test_job.id
        assert data["status"] == "interested"
        assert data["notes"] == "This looks interesting"
    
    async def test_update_favorite(self, client: AsyncClient, auth_headers, test_job):
        """Test updating favorite status."""
        # First add a favorite
        favorite_data = {
            "job_id": test_job.id,
            "status": "interested"
        }
        
        response = await client.post("/api/favorites", json=favorite_data, headers=auth_headers)
        favorite_id = response.json()["id"]
        
        # Update the favorite
        update_data = {
            "status": "applied",
            "notes": "Applied for this position"
        }
        
        response = await client.put(f"/api/favorites/{favorite_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "applied"
        assert data["notes"] == "Applied for this position"
    
    async def test_delete_favorite(self, client: AsyncClient, auth_headers, test_job):
        """Test removing favorite."""
        # First add a favorite
        favorite_data = {
            "job_id": test_job.id,
            "status": "interested"
        }
        
        response = await client.post("/api/favorites", json=favorite_data, headers=auth_headers)
        favorite_id = response.json()["id"]
        
        # Delete the favorite
        response = await client.delete(f"/api/favorites/{favorite_id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify favorite is deleted
        response = await client.get(f"/api/favorites/{favorite_id}", headers=auth_headers)
        assert response.status_code == 404


@pytest.mark.api
class TestMatchEndpoints:
    """Test matching endpoints."""
    
    async def test_match_resume_to_jobs(self, client: AsyncClient, auth_headers, test_resume, test_job):
        """Test matching resume to jobs."""
        match_data = {
            "resume_id": test_resume.id
        }
        
        response = await client.post("/api/match/", json=match_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert len(data["matches"]) > 0
        
        match = data["matches"][0]
        assert "score" in match
        assert "matching_keywords" in match
        assert "missing_keywords" in match
        assert "recommendation" in match
    
    async def test_match_resume_to_specific_job(self, client: AsyncClient, auth_headers, test_resume, test_job):
        """Test matching resume to specific job."""
        match_data = {
            "resume_id": test_resume.id,
            "job_id": test_job.id
        }
        
        response = await client.post("/api/match/", json=match_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert len(data["matches"]) == 1
        
        match = data["matches"][0]
        assert match["job"]["id"] == test_job.id
    
    async def test_match_resume_not_found(self, client: AsyncClient, auth_headers):
        """Test matching with non-existent resume."""
        match_data = {
            "resume_id": 99999
        }
        
        response = await client.post("/api/match/", json=match_data, headers=auth_headers)
        
        assert response.status_code == 404
        assert "Resume not found" in response.json()["detail"]
