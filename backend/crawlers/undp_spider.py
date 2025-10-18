"""Crawler for UNDP jobs."""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from crawlers.base_crawler import BaseCrawler


class UNDPSpider(BaseCrawler):
    """Spider for UNDP jobs website."""

    def __init__(self):
        super().__init__("UNDP")
        self.api_url = "https://jobs.undp.org/cj_view_jobs.cfm"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def crawl(self) -> Dict:
        """Crawl UNDP jobs website."""
        jobs_data = []

        try:
            # Make request to UNDP jobs page
            response = self.session.get(self.api_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Parse job listings (adjust selectors based on actual website)
            job_rows = soup.select("tr.job-row")  # Example selector

            for job_row in job_rows[:50]:  # Limit to first 50
                try:
                    job_data = self.parse_job_row(job_row)
                    if job_data:
                        jobs_data.append(job_data)
                except Exception as e:
                    print(f"Error parsing UNDP job: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error crawling UNDP: {str(e)}")

        # Save jobs to database
        saved_count = self.save_jobs(jobs_data)

        return {
            "organization": self.organization,
            "jobs_found": len(jobs_data),
            "jobs_saved": saved_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    def parse_job_row(self, row) -> Dict:
        """Parse a single job row."""
        # Template - adjust based on actual website structure
        cells = row.select("td")
        if len(cells) < 4:
            return None

        return {
            "title": cells[0].text.strip(),
            "organization": self.organization,
            "job_id": f"UNDP-{cells[0].get('data-id', '')}",
            "description": cells[1].text.strip() if len(cells) > 1 else "",
            "location": cells[2].text.strip() if len(cells) > 2 else "",
            "grade": cells[3].text.strip() if len(cells) > 3 else "",
            "apply_url": f"https://jobs.undp.org{cells[0].select_one('a').get('href', '')}",
            "posted_date": datetime.utcnow().date(),
            "source_url": self.api_url,
            "is_active": True
        }


def crawl_undp_sync():
    """Synchronous wrapper for Celery task."""
    spider = UNDPSpider()
    return spider.crawl()




