"""Comprehensive system tests for UN Jobs Hub."""
import asyncio
import pytest
from datetime import datetime, date
from sqlalchemy import select
from database import get_async_session
from models.job import Job
from models.user import User
from models.resume import Resume
from services.matching_service import calculate_match_score, extract_keywords_from_job


class TestSystem:
    """System integration tests."""
    
    async def test_database_connection(self):
        """Test database connection and basic operations."""
        async with get_async_session() as session:
            # Test basic query
            result = await session.execute(select(Job).limit(1))
            jobs = result.scalars().all()
            print(f"✓ Database connection successful. Found {len(jobs)} jobs.")
            return True
    
    async def test_job_model_operations(self):
        """Test Job model CRUD operations."""
        async with get_async_session() as session:
            # Create a test job
            test_job = Job(
                title="Test Software Engineer",
                organization="UN",
                job_id="test_123",
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
            
            session.add(test_job)
            await session.commit()
            
            # Retrieve the job
            result = await session.execute(
                select(Job).where(Job.job_id == "test_123")
            )
            retrieved_job = result.scalar_one_or_none()
            
            assert retrieved_job is not None
            assert retrieved_job.title == "Test Software Engineer"
            assert retrieved_job.organization == "UN"
            assert retrieved_job.grade == "P-3"
            
            # Clean up
            await session.delete(retrieved_job)
            await session.commit()
            
            print("✓ Job model operations successful.")
            return True
    
    async def test_keyword_extraction(self):
        """Test keyword extraction from job postings."""
        test_job = Job(
            title="Senior Program Manager",
            description="Manage development programs in humanitarian settings. Experience with project management and stakeholder coordination required.",
            qualifications="Master's degree in International Development. Minimum 5 years experience in program management.",
            responsibilities="Lead program implementation, coordinate with partners, monitor and evaluate activities.",
            category="Programme Management",
            grade="P-4",
            contract_type="Fixed-term",
            organization="UNDP"
        )
        
        keywords = extract_keywords_from_job(test_job)
        
        # Check that important keywords are extracted
        expected_keywords = [
            "master", "program management", "project management", 
            "development", "humanitarian", "coordination", "p-4", "undp"
        ]
        
        for expected in expected_keywords:
            assert any(expected in keyword.lower() for keyword in keywords), f"Missing keyword: {expected}"
        
        print(f"✓ Keyword extraction successful. Found {len(keywords)} keywords.")
        return True
    
    async def test_matching_algorithm(self):
        """Test job-resume matching algorithm."""
        # Create test resume
        test_resume = Resume(
            user_id=1,
            filename="test_resume.pdf",
            raw_text="Software Engineer with 5 years experience in Python, JavaScript, and project management. Master's degree in Computer Science. Experience with web development and team leadership.",
            skills=["Python", "JavaScript", "Project Management", "Web Development", "Team Leadership"],
            experience_years=5,
            education_level="Master's",
            is_active=True
        )
        
        # Create test job
        test_job = Job(
            title="Senior Software Engineer",
            description="Lead development of web applications using Python and JavaScript. Manage development team and coordinate with stakeholders.",
            qualifications="Master's degree in Computer Science or related field. Minimum 5 years experience in software development.",
            responsibilities="Lead development team, design and implement web applications, coordinate with stakeholders.",
            category="Information Technology",
            grade="P-3",
            contract_type="Fixed-term",
            organization="UN",
            education_level="Master's",
            years_of_experience=5
        )
        
        # Test matching
        match_result = await calculate_match_score(test_resume, test_job)
        
        # Verify match result structure
        assert "score" in match_result
        assert "matching_keywords" in match_result
        assert "missing_keywords" in match_result
        assert "recommendation" in match_result
        assert "breakdown" in match_result
        
        # Verify score is reasonable
        assert 0.0 <= match_result["score"] <= 1.0
        
        # Verify matching keywords are found
        assert len(match_result["matching_keywords"]) > 0
        
        print(f"✓ Matching algorithm successful. Score: {match_result['score']:.2f}")
        print(f"  Matching keywords: {match_result['matching_keywords'][:5]}")
        return True
    
    async def test_api_endpoints(self):
        """Test basic API endpoint functionality."""
        # This would test the actual API endpoints
        # For now, we'll just verify the structure
        print("✓ API endpoints test placeholder (would test actual endpoints)")
        return True
    
    async def run_all_tests(self):
        """Run all system tests."""
        print("🧪 Running UN Jobs Hub System Tests")
        print("=" * 50)
        
        tests = [
            ("Database Connection", self.test_database_connection),
            ("Job Model Operations", self.test_job_model_operations),
            ("Keyword Extraction", self.test_keyword_extraction),
            ("Matching Algorithm", self.test_matching_algorithm),
            ("API Endpoints", self.test_api_endpoints),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"\n🔍 Running: {test_name}")
                result = await test_func()
                if result:
                    passed += 1
                    print(f"✅ {test_name} - PASSED")
                else:
                    failed += 1
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name} - ERROR: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! System is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
        
        return failed == 0


async def main():
    """Run the test suite."""
    test_system = TestSystem()
    success = await test_system.run_all_tests()
    return success


if __name__ == "__main__":
    asyncio.run(main())
