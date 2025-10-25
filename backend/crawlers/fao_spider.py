"""Crawler for FAO (Food and Agriculture Organization) careers."""
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from crawlers.base_crawler import BaseCrawler
import time
import json


class FAOSpider(BaseCrawler):
    """Spider for FAO careers website."""

    def __init__(self):
        super().__init__("FAO")
        self.base_url = "https://www.fao.org"
        self.careers_url = f"{self.base_url}/employment/vacancies"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': f'{self.base_url}/employment',
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
            "%d %B %Y",      # 31 December 2025
            "%d %b %Y",      # 31 Dec 2025
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
            r'(\d+)\s*to\s*(\d+)\s*years?',  # Range like "3 to 5 years"
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
        
        if any(word in text_lower for word in ['phd', 'doctorate', 'doctoral', 'ph.d']):
            return "Doctorate"
        elif any(word in text_lower for word in ['master', 'masters', 'msc', 'ma', 'mba', 'm.s', 'm.a']):
            return "Master's"
        elif any(word in text_lower for word in ['bachelor', 'bachelors', 'bsc', 'ba', 'undergraduate', 'b.s', 'b.a']):
            return "Bachelor's"
        elif any(word in text_lower for word in ['diploma', 'certificate', 'associate', 'technical']):
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

    def fetch_job_details(self, job_url: str) -> Dict:
        """Fetch detailed information for a specific job."""
        try:
            response = self.session.get(job_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract detailed information
            description = ""
            responsibilities = ""
            qualifications = ""
            
            # Look for job description sections
            desc_selectors = [
                '.job-description',
                '.vacancy-description',
                '.job-details',
                '.content',
                'main',
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    break
            
            # Look for responsibilities section
            resp_keywords = ['responsibilities', 'duties', 'key functions', 'main tasks']
            for keyword in resp_keywords:
                resp_elem = soup.find(['h2', 'h3', 'h4'], string=re.compile(keyword, re.I))
                if resp_elem:
                    resp_content = resp_elem.find_next(['div', 'p', 'ul'])
                    if resp_content:
                        responsibilities = resp_content.get_text(strip=True)
                        break
            
            # Look for qualifications section
            qual_keywords = ['qualifications', 'requirements', 'competencies', 'skills']
            for keyword in qual_keywords:
                qual_elem = soup.find(['h2', 'h3', 'h4'], string=re.compile(keyword, re.I))
                if qual_elem:
                    qual_content = qual_elem.find_next(['div', 'p', 'ul'])
                    if qual_content:
                        qualifications = qual_content.get_text(strip=True)
                        break
            
            # Extract additional metadata
            grade = ""
            contract_type = ""
            category = ""
            
            # Look for grade information
            grade_elem = soup.find(string=re.compile(r'P-\d+|G-\d+|NO-\w+|L-\d+', re.I))
            if grade_elem:
                grade = grade_elem.strip()
            
            # Look for contract type
            contract_keywords = ['fixed-term', 'temporary', 'consultant', 'intern', 'staff']
            for keyword in contract_keywords:
                if keyword in description.lower():
                    contract_type = keyword.title()
                    break
            
            return {
                'description': description,
                'responsibilities': responsibilities,
                'qualifications': qualifications,
                'grade': grade,
                'contract_type': contract_type,
                'category': category,
            }
            
        except Exception as e:
            print(f"Error fetching FAO job details from {job_url}: {str(e)}")
            return {}

    def crawl(self, max_jobs: int = 50) -> Dict:
        """Crawl FAO careers website."""
        jobs_data = []
        
        try:
            response = self.session.get(self.careers_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for job listings in various possible selectors
            job_selectors = [
                '.vacancy-item',
                '.job-listing',
                '.career-item',
                '.job-card',
                'tr[data-job-id]',
                '.vacancy-row',
            ]
            
            job_elements = []
            for selector in job_selectors:
                elements = soup.select(selector)
                if elements:
                    job_elements = elements[:max_jobs]
                    break
            
            if not job_elements:
                # Try to find job links in the page
                job_links = soup.find_all('a', href=re.compile(r'/employment/|/vacancies/|/jobs/'))
                job_elements = job_links[:max_jobs]
            
            print(f"Found {len(job_elements)} job elements on FAO careers page")
            
            for i, job_elem in enumerate(job_elements):
                try:
                    job_data = self.parse_job_element(job_elem)
                    if job_data:
                        # Fetch detailed information if we have a job URL
                        if job_data.get('apply_url'):
                            details = self.fetch_job_details(job_data['apply_url'])
                            job_data.update(details)
                        
                        jobs_data.append(job_data)
                        print(f"Parsed: {job_data['title']} ({job_data['organization']}) - {job_data.get('grade', 'N/A')}")
                    
                    # Add delay to avoid being blocked
                    if i % 3 == 0:
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"Error parsing FAO job: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error crawling FAO: {str(e)}")

        # Save jobs to database
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
            
            # Extract location
            location = ''
            location_elem = job_elem.find(['span', 'div'], class_=re.compile(r'location|place|city|duty', re.I))
            if location_elem:
                location = location_elem.get_text(strip=True)
            
            # Extract deadline
            deadline = None
            deadline_elem = job_elem.find(['span', 'div'], class_=re.compile(r'deadline|closing|date', re.I))
            if deadline_elem:
                deadline_text = deadline_elem.get_text(strip=True)
                deadline = self.parse_date(deadline_text)
            
            # Extract grade
            grade = ''
            grade_elem = job_elem.find(string=re.compile(r'P-\d+|G-\d+|NO-\w+|L-\d+', re.I))
            if grade_elem:
                grade = grade_elem.strip()
            
            # Extract contract type
            contract_type = ''
            contract_elem = job_elem.find(string=re.compile(r'fixed-term|temporary|consultant|intern|staff', re.I))
            if contract_elem:
                contract_type = contract_elem.strip().title()
            
            # Generate job ID
            job_id = f"fao_{hash(title + location)}"
            
            return {
                'job_id': job_id,
                'title': title,
                'organization': 'FAO',
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
                'deadline': deadline,
                'posted_date': datetime.utcnow().date(),
                'source_url': detail_url,
                'is_active': True,
            }
            
        except Exception as e:
            print(f"Error parsing FAO job element: {str(e)}")
            return None


def crawl_fao_sync(max_jobs: int = 50):
    """Synchronous wrapper for FAO crawler."""
    spider = FAOSpider()
    return spider.crawl(max_jobs=max_jobs)


if __name__ == "__main__":
    result = crawl_fao_sync(max_jobs=20)
    print(f"FAO Crawler Result: {result}")
