"""Tests for service layer."""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import date

from services.matching_service import (
    calculate_match_score,
    extract_keywords_from_job,
    get_ai_recommendation
)
from services.resume_parser import (
    parse_resume,
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_skills,
    extract_experience_years,
    extract_education_level
)
from models.job import Job
from models.resume import Resume


@pytest.mark.service
class TestMatchingService:
    """Test matching service."""
    
    async def test_calculate_match_score_perfect_match(self):
        """Test matching with perfect alignment."""
        resume = Resume(
            user_id=1,
            filename="test.pdf",
            raw_text="Software Engineer with 5 years experience in Python, JavaScript, and project management. Master's degree in Computer Science.",
            skills=["Python", "JavaScript", "Project Management", "Leadership"],
            experience_years=5,
            education_level="Master's",
            is_active=True
        )
        
        job = Job(
            title="Senior Software Engineer",
            description="Lead development using Python and JavaScript. Manage development team.",
            qualifications="Master's degree in Computer Science. 5+ years experience.",
            responsibilities="Lead team, develop applications, coordinate stakeholders.",
            category="Information Technology",
            grade="P-3",
            contract_type="Fixed-term",
            organization="UN",
            education_level="Master's",
            years_of_experience=5,
            apply_url="https://example.com",
            deadline=date(2025, 12, 31),
            posted_date=date.today(),
            source_url="https://example.com",
            is_active=True
        )
        
        result = await calculate_match_score(resume, job)
        
        assert "score" in result
        assert "matching_keywords" in result
        assert "missing_keywords" in result
        assert "recommendation" in result
        assert "breakdown" in result
        
        # Should have high score for perfect match
        assert result["score"] > 0.8
        assert len(result["matching_keywords"]) > 0
    
    async def test_calculate_match_score_poor_match(self):
        """Test matching with poor alignment."""
        resume = Resume(
            user_id=1,
            filename="test.pdf",
            raw_text="Marketing specialist with 2 years experience in social media and content creation.",
            skills=["Social Media", "Content Creation", "Marketing"],
            experience_years=2,
            education_level="Bachelor's",
            is_active=True
        )
        
        job = Job(
            title="Senior Software Engineer",
            description="Lead development using Python and JavaScript. Manage development team.",
            qualifications="Master's degree in Computer Science. 5+ years experience.",
            responsibilities="Lead team, develop applications, coordinate stakeholders.",
            category="Information Technology",
            grade="P-3",
            contract_type="Fixed-term",
            organization="UN",
            education_level="Master's",
            years_of_experience=5,
            apply_url="https://example.com",
            deadline=date(2025, 12, 31),
            posted_date=date.today(),
            source_url="https://example.com",
            is_active=True
        )
        
        result = await calculate_match_score(resume, job)
        
        # Should have low score for poor match
        assert result["score"] < 0.5
        assert len(result["missing_keywords"]) > len(result["matching_keywords"])
    
    def test_extract_keywords_from_job(self):
        """Test keyword extraction from job."""
        job = Job(
            title="Program Manager",
            description="Manage development programs in humanitarian settings. Experience with project management required.",
            qualifications="Master's degree in International Development. Minimum 5 years experience.",
            responsibilities="Lead program implementation, coordinate with partners.",
            category="Programme Management",
            grade="P-4",
            contract_type="Fixed-term",
            organization="UNDP",
            apply_url="https://example.com",
            deadline=date(2025, 12, 31),
            posted_date=date.today(),
            source_url="https://example.com",
            is_active=True
        )
        
        keywords = extract_keywords_from_job(job)
        
        # Should extract important keywords
        expected_keywords = [
            "program management", "project management", "master", 
            "development", "humanitarian", "p-4", "undp"
        ]
        
        keyword_lower = [k.lower() for k in keywords]
        for expected in expected_keywords:
            assert any(expected in kw for kw in keyword_lower), f"Missing keyword: {expected}"
    
    @patch('services.matching_service.openai_available', True)
    async def test_get_ai_recommendation(self, mock_openai):
        """Test AI recommendation generation."""
        resume = Resume(
            user_id=1,
            filename="test.pdf",
            raw_text="Software Engineer with 3 years experience.",
            skills=["Python", "JavaScript"],
            experience_years=3,
            education_level="Bachelor's",
            is_active=True
        )
        
        job = Job(
            title="Senior Software Engineer",
            description="Lead development team.",
            qualifications="Master's degree. 5+ years experience.",
            responsibilities="Lead team.",
            category="IT",
            grade="P-3",
            contract_type="Fixed-term",
            organization="UN",
            education_level="Master's",
            years_of_experience=5,
            apply_url="https://example.com",
            deadline=date(2025, 12, 31),
            posted_date=date.today(),
            source_url="https://example.com",
            is_active=True
        )
        
        with patch('services.matching_service.AsyncOpenAI') as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_openai.chat_completions_create()
            )
            
            recommendation = await get_ai_recommendation(resume, job, 0.6, ["Leadership", "Team Management"])
            
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0


@pytest.mark.service
class TestResumeParser:
    """Test resume parser service."""
    
    async def test_parse_resume_pdf(self, temp_file):
        """Test parsing PDF resume."""
        with patch('services.resume_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = "Software Engineer with 5 years experience in Python and JavaScript. Master's degree in Computer Science."
            
            result = await parse_resume(temp_file, "application/pdf")
            
            assert "raw_text" in result
            assert "skills" in result
            assert "experience_years" in result
            assert "education_level" in result
            assert "structured_data" in result
            
            mock_extract.assert_called_once_with(temp_file)
    
    async def test_parse_resume_docx(self, temp_file):
        """Test parsing DOCX resume."""
        with patch('services.resume_parser.extract_text_from_docx') as mock_extract:
            mock_extract.return_value = "Project Manager with 7 years experience in team leadership and strategic planning."
            
            result = await parse_resume(temp_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
            assert "raw_text" in result
            assert "skills" in result
            assert "experience_years" in result
            assert "education_level" in result
            
            mock_extract.assert_called_once_with(temp_file)
    
    def test_extract_skills(self):
        """Test skill extraction."""
        text = "Experienced in Python, JavaScript, React, Node.js, SQL, and project management."
        
        skills = extract_skills(text)
        
        expected_skills = ["Python", "JavaScript", "React", "Node.js", "SQL", "Project Management"]
        
        for skill in expected_skills:
            assert any(skill.lower() in skill_found.lower() for skill_found in skills), f"Missing skill: {skill}"
    
    def test_extract_experience_years(self):
        """Test experience years extraction."""
        test_cases = [
            ("5 years of experience", 5),
            ("7+ years in software development", 7),
            ("Over 10 years experience", 10),
            ("3-5 years of relevant experience", 4),  # Average
            ("No experience mentioned", None)
        ]
        
        for text, expected in test_cases:
            result = extract_experience_years(text)
            if expected is None:
                assert result is None or result == 0
            else:
                assert result == expected or abs(result - expected) <= 1
    
    def test_extract_education_level(self):
        """Test education level extraction."""
        test_cases = [
            ("Master's degree in Computer Science", "Master's"),
            ("Bachelor of Science", "Bachelor's"),
            ("PhD in Engineering", "PhD"),
            ("High school diploma", "High School"),
            ("No education mentioned", None)
        ]
        
        for text, expected in test_cases:
            result = extract_education_level(text)
            assert result == expected
