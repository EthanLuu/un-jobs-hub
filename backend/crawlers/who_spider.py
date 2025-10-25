"""Crawler for WHO (World Health Organization) careers."""
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from crawlers.base_crawler import BaseCrawler
import time
import json


class WHOSpider(BaseCrawler):
    """Spider for WHO careers website."""

    def __init__(self):
        super().__init__("WHO")
        self.base_url = "https://www.who.int"
        self.careers_url = f"{self.base_url}/careers"
        self.api_url = f"{self.base_url}/api/v1/careers"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': f'{self.base_url}/careers',
        })

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None

        date_str = date_str.strip()
        
        # Try common date formats
        formats = [
            "%Y-%m-%d",      # 2025-12-31
            "%d-%m-%Y",      # 31-12-2025
            "%d/%m/%Y",      # 31/12/2025
            "%B %d, %Y",     # December 31, 2025
            "%b %d, %Y",     # Dec 31, 2025
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

        # Look for patterns like "5 years", "3+ years", "minimum 2 years"
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?',  # Range like "3-5 years"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    # For range patterns, return the minimum
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
        elif any(word in text_lower for word in ['bachelor', 'bachelors', 'bsc', 'ba', 'undergraduate']):
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

        # Common language patterns
        language_patterns = {
            'en': ['english', 'anglais'],
            'fr': ['french', 'français', 'francais'],
            'es': ['spanish', 'español', 'espanol'],
            'ar': ['arabic', 'arabe'],
            'zh': ['chinese', 'chinois', 'mandarin'],
            'ru': ['russian', 'russe'],
            'de': ['german', 'allemand', 'deutsch'],
            'pt': ['portuguese', 'portugais'],
            'it': ['italian', 'italien'],
            'ja': ['japanese', 'japonais'],
        }

        for lang_code, patterns in language_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    # Determine requirement level
                    if any(word in text_lower for word in ['required', 'essential', 'mandatory', 'obligatoire']):
                        languages[lang_code] = "required"
                    elif any(word in text_lower for word in ['desirable', 'preferred', 'advantage', 'souhaitable']):
                        languages[lang_code] = "desirable"
                    else:
                        languages[lang_code] = "required"  # Default to required if mentioned

        return languages

    def crawl(self, max_jobs: int = 50) -> Dict:
        """Crawl WHO careers website."""
        jobs_data = []
        
        try:
            # Try API first
            try:
                response = self.session.get(self.api_url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    jobs = data.get('jobs', [])[:max_jobs]
                    
                    for job in jobs:
                        try:
                            job_data = self.parse_api_job(job)
                            if job_data:
                                jobs_data.append(job_data)
                        except Exception as e:
                            print(f"Error parsing WHO API job: {str(e)}")
                            continue
                    
                    print(f"Successfully crawled {len(jobs_data)} jobs from WHO API")
                else:
                    raise Exception(f"API returned status {response.status_code}")
                    
            except Exception as api_error:
                print(f"WHO API failed: {str(api_error)}, trying web scraping...")
                
                # Fallback to web scraping
                response = self.session.get(self.careers_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Look for job listings in various possible selectors
                job_selectors = [
                    '.job-listing',
                    '.vacancy-item',
                    '.career-item',
                    '.job-card',
                    '[data-job-id]',
                ]
                
                job_elements = []
                for selector in job_selectors:
                    elements = soup.select(selector)
                    if elements:
                        job_elements = elements[:max_jobs]
                        break
                
                if not job_elements:
                    # Try to find job links in the page
                    job_links = soup.find_all('a', href=re.compile(r'/careers/|/jobs/|/vacancies/'))
                    job_elements = job_links[:max_jobs]
                
                for i, job_elem in enumerate(job_elements):
                    try:
                        job_data = self.parse_web_job(job_elem)
                        if job_data:
                            jobs_data.append(job_data)
                        
                        # Add delay to avoid being blocked
                        if i % 5 == 0:
                            time.sleep(1)
                            
                    except Exception as e:
                        print(f"Error parsing WHO web job: {str(e)}")
                        continue

        except Exception as e:
            print(f"Error crawling WHO: {str(e)}")

        # Save jobs to database
        saved_count = self.save_jobs(jobs_data)

        return {
            "organization": self.organization,
            "jobs_found": len(jobs_data),
            "jobs_saved": saved_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    def parse_api_job(self, job: Dict) -> Dict:
        """Parse job data from API response."""
        try:
            # Extract basic information
            title = job.get('title', '')
            description = job.get('description', '')
            location = job.get('location', '')
            organization = job.get('organization', 'WHO')
            
            # Extract additional details
            grade = job.get('grade', '')
            contract_type = job.get('contractType', '')
            category = job.get('category', '')
            
            # Parse dates
            deadline = None
            if job.get('deadline'):
                deadline = self.parse_date(job.get('deadline'))
            
            posted_date = None
            if job.get('postedDate'):
                posted_date = self.parse_date(job.get('postedDate'))
            
            # Extract requirements
            requirements_text = job.get('requirements', '') or description
            years_experience = self.extract_experience_years(requirements_text)
            education_level = self.extract_education_level(requirements_text)
            language_requirements = self.extract_language_requirements(requirements_text)
            
            # Generate job ID
            job_id = job.get('id', '')
            if not job_id:
                job_id = f"who_{hash(title + location)}"
            
            # Build apply URL
            apply_url = job.get('applyUrl', '')
            if not apply_url and job.get('id'):
                apply_url = f"{self.base_url}/careers/job/{job.get('id')}"
            
            return {
                'job_id': job_id,
                'title': title,
                'organization': organization,
                'description': description,
                'location': location,
                'duty_station': location,
                'grade': grade,
                'contract_type': contract_type,
                'category': category,
                'years_of_experience': years_experience,
                'education_level': education_level,
                'language_requirements': language_requirements,
                'apply_url': apply_url,
                'deadline': deadline,
                'posted_date': posted_date or datetime.utcnow().date(),
                'source_url': job.get('url', ''),
                'is_active': True,
            }
            
        except Exception as e:
            print(f"Error parsing WHO API job: {str(e)}")
            return None

    def parse_web_job(self, job_elem) -> Dict:
        """Parse job data from web scraping."""
        try:
            # Extract title
            title_elem = job_elem.find(['h1', 'h2', 'h3', 'h4', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            if not title:
                return None
            
            # Extract link
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
            
            # Try to extract additional info from the element
            location = ''
            grade = ''
            contract_type = ''
            
            # Look for location info
            location_elem = job_elem.find(['span', 'div'], class_=re.compile(r'location|place|city', re.I))
            if location_elem:
                location = location_elem.get_text(strip=True)
            
            # Look for grade info
            grade_elem = job_elem.find(['span', 'div'], class_=re.compile(r'grade|level|p-\d+|g-\d+', re.I))
            if grade_elem:
                grade = grade_elem.get_text(strip=True)
            
            # Generate job ID
            job_id = f"who_{hash(title + location)}"
            
            return {
                'job_id': job_id,
                'title': title,
                'organization': 'WHO',
                'description': '',  # Will be filled when fetching details
                'location': location,
                'duty_station': location,
                'grade': grade,
                'contract_type': contract_type,
                'category': '',
                'years_of_experience': None,
                'education_level': None,
                'language_requirements': {},
                'apply_url': detail_url,
                'deadline': None,
                'posted_date': datetime.utcnow().date(),
                'source_url': detail_url,
                'is_active': True,
            }
            
        except Exception as e:
            print(f"Error parsing WHO web job: {str(e)}")
            return None


def crawl_who_sync(max_jobs: int = 50):
    """Synchronous wrapper for WHO crawler."""
    spider = WHOSpider()
    return spider.crawl(max_jobs=max_jobs)


if __name__ == "__main__":
    result = crawl_who_sync(max_jobs=20)
    print(f"WHO Crawler Result: {result}")
