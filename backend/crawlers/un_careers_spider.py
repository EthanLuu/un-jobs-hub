"""Crawler for careers.un.org."""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from crawlers.base_crawler import BaseCrawler


class UNCareersSpider(BaseCrawler):
    """Spider for UN Careers website."""

    def __init__(self):
        super().__init__("UN")
        self.base_url = "https://careers.un.org"
        self.search_url = f"{self.base_url}/lbw/Home.aspx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def crawl(self) -> Dict:
        """Crawl UN Careers website using requests."""
        jobs_data = []

        try:
            # Get page content with requests
            response = self.session.get(self.search_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Parse job listings (adjust selectors based on actual website structure)
            job_elements = soup.select(".vacancy-item")  # Example selector

            for job_elem in job_elements[:50]:  # Limit to first 50 jobs
                try:
                    job_data = self.parse_job_element(job_elem)
                    if job_data:
                        jobs_data.append(job_data)
                except Exception as e:
                    print(f"Error parsing job: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error crawling UN Careers: {str(e)}")

        # Save jobs to database
        saved_count = self.save_jobs(jobs_data)

        return {
            "organization": self.organization,
            "jobs_found": len(jobs_data),
            "jobs_saved": saved_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    def parse_job_element(self, element) -> Dict:
        """Parse a single job element."""
        # This is a template - adjust based on actual website structure
        title_elem = element.select_one(".job-title")
        location_elem = element.select_one(".job-location")
        deadline_elem = element.select_one(".deadline")
        link_elem = element.select_one("a")

        if not title_elem or not link_elem:
            return None

        return {
            "title": title_elem.text.strip(),
            "organization": self.organization,
            "job_id": f"UN-{link_elem.get('href', '').split('/')[-1]}",
            "description": element.select_one(".job-description").text.strip() if element.select_one(".job-description") else "",
            "location": location_elem.text.strip() if location_elem else "",
            "apply_url": f"{self.base_url}{link_elem.get('href', '')}",
            "deadline": self.parse_date(deadline_elem.text.strip()) if deadline_elem else None,
            "posted_date": datetime.utcnow().date(),
            "source_url": self.search_url,
            "is_active": True
        }

    def parse_date(self, date_str: str):
        """Parse date string to date object."""
        try:
            # Try common date formats
            for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
        except Exception:
            pass
        return None


def crawl_un_careers_sync():
    """Synchronous wrapper for Celery task."""
    spider = UNCareersSpider()
    return spider.crawl()




