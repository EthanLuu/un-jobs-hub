"""Crawler for UNOPS (United Nations Office for Project Services) careers."""
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from crawlers.base_crawler import BaseCrawler
import time


class UNOPSSpider(BaseCrawler):
    """Spider for UNOPS careers website."""

    def __init__(self):
        super().__init__("UNOPS")
        self.base_url = "https://jobs.unops.org"
        self.careers_url = f"{self.base_url}/Pages/JobSearch.aspx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None

        date_str = date_str.strip()
        formats = [
            "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", 
            "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def extract_experience_years(self, text: str) -> Optional[int]:
        """Extract years of experience from text."""
        if not text:
            return None

        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    return int(matches[0][0])
                else:
                    return int(matches[0])
        return None

    def extract_education_level(self, text: str) -> Optional[str]:
        """Extract education level from text."""
        if not text:
            return None

        text_lower = text.lower()
        
        if any(word in text_lower for word in ['phd', 'doctorate', 'doctoral']):
            return "Doctorate"
        elif any(word in text_lower for word in ['master', 'masters', 'msc', 'ma', 'mba']):
            return "Master's"
        elif any(word in text_lower for word in ['bachelor', 'bachelors', 'bsc', 'ba']):
            return "Bachelor's"
        elif any(word in text_lower for word in ['diploma', 'certificate', 'associate']):
            return "Diploma/Certificate"
        return None

    def extract_language_requirements(self, text: str) -> Dict[str, str]:
        """Extract language requirements from text."""
        if not text:
            return {}

        languages = {}
        text_lower = text.lower()

        language_patterns = {
            'en': ['english', 'anglais'],
            'fr': ['french', 'français', 'francais'],
            'es': ['spanish', 'español', 'espanol'],
            'ar': ['arabic', 'arabe'],
            'zh': ['chinese', 'chinois', 'mandarin'],
        }

        for lang_code, patterns in language_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    if any(word in text_lower for word in ['required', 'essential', 'mandatory']):
                        languages[lang_code] = "required"
                    elif any(word in text_lower for word in ['desirable', 'preferred', 'advantage']):
                        languages[lang_code] = "desirable"
                    else:
                        languages[lang_code] = "required"
        return languages

    def crawl(self, max_jobs: int = 50) -> Dict:
        """Crawl UNOPS careers website."""
        jobs_data = []
        
        try:
            response = self.session.get(self.careers_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for job listings
            job_selectors = [
                '.job-item', '.vacancy-item', '.job-listing', 
                '.career-item', 'tr[data-job-id]', '.job-row'
            ]
            
            job_elements = []
            for selector in job_selectors:
                elements = soup.select(selector)
                if elements:
                    job_elements = elements[:max_jobs]
                    break
            
            if not job_elements:
                job_links = soup.find_all('a', href=re.compile(r'/Pages/JobDetails|/job/'))
                job_elements = job_links[:max_jobs]
            
            print(f"Found {len(job_elements)} job elements on UNOPS careers page")
            
            for i, job_elem in enumerate(job_elements):
                try:
                    job_data = self.parse_job_element(job_elem)
                    if job_data:
                        jobs_data.append(job_data)
                        print(f"Parsed: {job_data['title']} ({job_data['organization']}) - {job_data.get('grade', 'N/A')}")
                    
                    if i % 3 == 0:
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"Error parsing UNOPS job: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error crawling UNOPS: {str(e)}")

        saved_count = self.save_jobs(jobs_data)
        return {
            "organization": self.organization,
            "jobs_found": len(jobs_data),
            "jobs_saved": saved_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    def parse_job_element(self, job_elem) -> Dict:
        """Parse a single job element."""
        try:
            title_elem = job_elem.find(['h1', 'h2', 'h3', 'h4', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            if not title:
                return None
            
            link_elem = job_elem.find('a') if job_elem.name != 'a' else job_elem
            detail_url = ''
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('/'):
                    detail_url = f"{self.base_url}{href}"
                elif href.startswith('http'):
                    detail_url = href
                else:
                    detail_url = f"{self.base_url}/{href}"
            
            location = ''
            location_elem = job_elem.find(['span', 'div'], class_=re.compile(r'location|place|city', re.I))
            if location_elem:
                location = location_elem.get_text(strip=True)
            
            deadline = None
            deadline_elem = job_elem.find(['span', 'div'], class_=re.compile(r'deadline|closing', re.I))
            if deadline_elem:
                deadline_text = deadline_elem.get_text(strip=True)
                deadline = self.parse_date(deadline_text)
            
            grade = ''
            grade_elem = job_elem.find(string=re.compile(r'P-\d+|G-\d+|NO-\w+|L-\d+', re.I))
            if grade_elem:
                grade = grade_elem.strip()
            
            job_id = f"unops_{hash(title + location)}"
            
            return {
                'job_id': job_id,
                'title': title,
                'organization': 'UNOPS',
                'description': '',
                'location': location,
                'duty_station': location,
                'grade': grade,
                'contract_type': '',
                'category': '',
                'years_of_experience': None,
                'education_level': None,
                'language_requirements': {},
                'apply_url': detail_url,
                'deadline': deadline,
                'posted_date': datetime.utcnow().date(),
                'source_url': detail_url,
                'is_active': True,
            }
            
        except Exception as e:
            print(f"Error parsing UNOPS job element: {str(e)}")
            return None


def crawl_unops_sync(max_jobs: int = 50):
    """Synchronous wrapper for UNOPS crawler."""
    spider = UNOPSSpider()
    return spider.crawl(max_jobs=max_jobs)


if __name__ == "__main__":
    result = crawl_unops_sync(max_jobs=20)
    print(f"UNOPS Crawler Result: {result}")
