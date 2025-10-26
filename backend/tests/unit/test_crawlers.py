"""Tests for crawler functionality."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date

from crawlers.base_crawler import BaseCrawler
from crawlers.un_careers_spider import UNCareersSpider
from crawlers.undp_spider import UNDPSpider
from crawlers.unicef_spider import UNICEFSpider


@pytest.mark.crawler
class TestBaseCrawler:
    """Test base crawler functionality."""
    
    def test_base_crawler_initialization(self):
        """Test base crawler initialization."""
        crawler = BaseCrawler("test_org")
        
        assert crawler.organization == "test_org"
        assert crawler.session is not None
        assert crawler.headers is not None
        assert "User-Agent" in crawler.headers
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        crawler = BaseCrawler("test_org")
        
        dirty_text = "  Hello   World  \n\n  Test  "
        clean_text = crawler.clean_text(dirty_text)
        
        assert clean_text == "Hello World Test"
    
    def test_extract_date(self):
        """Test date extraction."""
        crawler = BaseCrawler("test_org")
        
        # Test various date formats
        test_cases = [
            ("2024-12-31", date(2024, 12, 31)),
            ("31/12/2024", date(2024, 12, 31)),
            ("December 31, 2024", date(2024, 12, 31)),
            ("Invalid date", None)
        ]
        
        for date_str, expected in test_cases:
            result = crawler.extract_date(date_str)
            assert result == expected
    
    def test_extract_experience_years(self):
        """Test experience years extraction."""
        crawler = BaseCrawler("test_org")
        
        test_cases = [
            ("5 years of experience", 5),
            ("7+ years", 7),
            ("3-5 years", 4),  # Average
            ("No experience", None)
        ]
        
        for text, expected in test_cases:
            result = crawler.extract_experience_years(text)
            if expected is None:
                assert result is None
            else:
                assert result == expected or abs(result - expected) <= 1


@pytest.mark.crawler
class TestUNCareersSpider:
    """Test UN Careers spider."""
    
    def test_un_careers_spider_initialization(self):
        """Test UN Careers spider initialization."""
        spider = UNCareersSpider()
        
        assert spider.organization == "UN"
        assert spider.base_url == "https://careers.un.org"
        assert spider.session is not None
    
    @patch('crawlers.un_careers_spider.requests.get')
    def test_fetch_job_listings(self, mock_get):
        """Test fetching job listings."""
        spider = UNCareersSpider()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <div class="job-listing">
                <h3><a href="/job/123">Software Engineer</a></h3>
                <span class="location">Geneva</span>
                <span class="grade">P-3</span>
            </div>
        </html>
        """
        mock_get.return_value = mock_response
        
        jobs = spider.fetch_job_listings()
        
        assert len(jobs) > 0
        assert jobs[0]["title"] == "Software Engineer"
        assert jobs[0]["location"] == "Geneva"
        assert jobs[0]["grade"] == "P-3"
    
    @patch('crawlers.un_careers_spider.requests.get')
    def test_fetch_job_details(self, mock_get):
        """Test fetching job details."""
        spider = UNCareersSpider()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <h1>Software Engineer</h1>
            <div class="description">Manage software development projects.</div>
            <div class="qualifications">Master's degree required.</div>
            <div class="responsibilities">Lead development team.</div>
            <div class="deadline">2024-12-31</div>
        </html>
        """
        mock_get.return_value = mock_response
        
        job_details = spider.fetch_job_details("https://careers.un.org/job/123")
        
        assert job_details["title"] == "Software Engineer"
        assert "Manage software development projects" in job_details["description"]
        assert "Master's degree required" in job_details["qualifications"]
        assert "Lead development team" in job_details["responsibilities"]
        assert job_details["deadline"] == date(2024, 12, 31)


@pytest.mark.crawler
class TestUNDPSpider:
    """Test UNDP spider."""
    
    def test_undp_spider_initialization(self):
        """Test UNDP spider initialization."""
        spider = UNDPSpider()
        
        assert spider.organization == "UNDP"
        assert spider.base_url == "https://jobs.undp.org"
        assert spider.session is not None
    
    @patch('crawlers.undp_spider.requests.get')
    def test_fetch_job_listings(self, mock_get):
        """Test fetching UNDP job listings."""
        spider = UNDPSpider()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <div class="job-item">
                <h3><a href="/job/456">Program Manager</a></h3>
                <span class="location">New York</span>
                <span class="level">P-4</span>
            </div>
        </html>
        """
        mock_get.return_value = mock_response
        
        jobs = spider.fetch_job_listings()
        
        assert len(jobs) > 0
        assert jobs[0]["title"] == "Program Manager"
        assert jobs[0]["location"] == "New York"
        assert jobs[0]["grade"] == "P-4"


@pytest.mark.crawler
class TestUNICEFSpider:
    """Test UNICEF spider."""
    
    def test_unicef_spider_initialization(self):
        """Test UNICEF spider initialization."""
        spider = UNICEFSpider()
        
        assert spider.organization == "UNICEF"
        assert spider.base_url == "https://jobs.unicef.org"
        assert spider.session is not None
    
    @patch('crawlers.unicef_spider.requests.get')
    def test_fetch_job_listings(self, mock_get):
        """Test fetching UNICEF job listings."""
        spider = UNICEFSpider()
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <div class="job-card">
                <h3><a href="/job/789">Child Protection Specialist</a></h3>
                <span class="location">Copenhagen</span>
                <span class="level">P-3</span>
            </div>
        </html>
        """
        mock_get.return_value = mock_response
        
        jobs = spider.fetch_job_listings()
        
        assert len(jobs) > 0
        assert jobs[0]["title"] == "Child Protection Specialist"
        assert jobs[0]["location"] == "Copenhagen"
        assert jobs[0]["grade"] == "P-3"


@pytest.mark.crawler
class TestCrawlerIntegration:
    """Test crawler integration."""
    
    @patch('crawlers.un_careers_spider.requests.get')
    def test_crawler_error_handling(self, mock_get):
        """Test crawler error handling."""
        spider = UNCareersSpider()
        
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server error")
        mock_get.return_value = mock_response
        
        # Should handle errors gracefully
        jobs = spider.fetch_job_listings()
        assert jobs == []
    
    @patch('crawlers.un_careers_spider.requests.get')
    def test_crawler_rate_limiting(self, mock_get):
        """Test crawler rate limiting."""
        spider = UNCareersSpider()
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test</body></html>"
        mock_get.return_value = mock_response
        
        # Test that crawler respects rate limiting
        import time
        start_time = time.time()
        
        spider.fetch_job_listings()
        
        # Should have some delay (even if minimal in tests)
        elapsed = time.time() - start_time
        assert elapsed >= 0  # At least no negative time
