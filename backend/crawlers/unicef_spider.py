"""Crawler for UNICEF careers."""
import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict
from crawlers.base_crawler import BaseCrawler


class UNICEFSpider(BaseCrawler):
    """Spider for UNICEF careers website."""
    
    def __init__(self):
        super().__init__("UNICEF")
        self.careers_url = "https://www.unicef.org/careers/search-jobs"
    
    async def crawl_async(self) -> Dict:
        """Crawl UNICEF careers website."""
        jobs_data = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(self.careers_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Parse job listings (adjust selectors based on actual website)
                job_cards = soup.select(".job-card")  # Example selector
                
                for job_card in job_cards[:50]:  # Limit to first 50
                    try:
                        job_data = self.parse_job_card(job_card)
                        if job_data:
                            jobs_data.append(job_data)
                    except Exception as e:
                        print(f"Error parsing UNICEF job: {str(e)}")
                        continue
                
            except Exception as e:
                print(f"Error crawling UNICEF: {str(e)}")
        
        # Save jobs to database
        saved_count = self.save_jobs(jobs_data)
        
        return {
            "organization": self.organization,
            "jobs_found": len(jobs_data),
            "jobs_saved": saved_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def parse_job_card(self, card) -> Dict:
        """Parse a single job card."""
        title_elem = card.select_one(".job-title")
        if not title_elem:
            return None
        
        return {
            "title": title_elem.text.strip(),
            "organization": self.organization,
            "job_id": f"UNICEF-{card.get('data-job-id', '')}",
            "description": card.select_one(".job-description").text.strip() if card.select_one(".job-description") else "",
            "location": card.select_one(".job-location").text.strip() if card.select_one(".job-location") else "",
            "apply_url": card.select_one("a").get("href", "") if card.select_one("a") else "",
            "posted_date": datetime.utcnow().date(),
            "source_url": self.careers_url,
            "is_active": True
        }


def crawl_unicef_sync():
    """Synchronous wrapper for Celery task."""
    spider = UNICEFSpider()
    return asyncio.run(spider.crawl_async())



