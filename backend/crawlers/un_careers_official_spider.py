"""Crawler for official UN Careers website (careers.un.org)."""
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from crawlers.base_crawler import BaseCrawler
import time


class UNCareersOfficialSpider(BaseCrawler):
    """Spider for official UN Careers website (careers.un.org/jobopening)."""

    def __init__(self):
        super().__init__("UN")
        self.base_url = "https://careers.un.org"
        self.job_opening_url = f"{self.base_url}/jobopening"
        self.session = requests.Session()
        # Use comprehensive headers to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object.

        Supports formats:
        - DD-MMM-YYYY (e.g., "31-Dec-2025")
        - DD/MM/YYYY
        - YYYY-MM-DD
        - Month DD, YYYY (e.g., "December 31, 2025")
        """
        if not date_str:
            return None

        date_str = date_str.strip()

        # Try common date formats
        formats = [
            "%d-%b-%Y",      # 31-Dec-2025
            "%d-%B-%Y",      # 31-December-2025
            "%d/%m/%Y",      # 31/12/2025
            "%Y-%m-%d",      # 2025-12-31
            "%B %d, %Y",     # December 31, 2025
            "%d %B %Y",      # 31 December 2025
            "%m/%d/%Y",      # 12/31/2025
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def read_page(self, url: str, retry: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse HTML page with retry logic."""
        for attempt in range(retry):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}/{retry} failed for {url}: {str(e)}")
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"Failed to fetch {url} after {retry} attempts")
                    return None
        return None

    def fetch_job_detail(self, job_url: str) -> Dict:
        """Fetch detailed job information from job detail page."""
        html = self.read_page(job_url)
        if not html:
            return {}

        detail = {}

        # Extract job title
        title_elem = html.select_one('h1.page-title, h1, .job-title')
        if title_elem:
            detail['title'] = title_elem.get_text(strip=True)

        # Extract job description sections
        # UN Careers typically has structured sections
        description_parts = []
        responsibilities = []
        qualifications = []

        # Find main content area
        content_area = html.select_one('.view-content, .job-content, .vacancy-content')
        if content_area:
            # Extract all text sections
            sections = content_area.find_all(['div', 'section', 'p', 'ul', 'ol'])
            current_section = ""

            for section in sections:
                text = section.get_text(strip=True)
                text_lower = text.lower()

                # Check for section headers
                header = section.find(['h2', 'h3', 'h4', 'strong', 'b'])
                if header:
                    current_section = header.get_text(strip=True).lower()

                # Categorize content
                if any(keyword in current_section for keyword in ['responsibilit', 'duties', 'accountabilit', 'key functions']):
                    if section.name in ['ul', 'ol']:
                        items = section.find_all('li')
                        responsibilities.extend([item.get_text(strip=True) for item in items])
                elif any(keyword in current_section for keyword in ['qualification', 'requirement', 'competenc', 'education', 'experience']):
                    if section.name in ['ul', 'ol']:
                        items = section.find_all('li')
                        qualifications.extend([item.get_text(strip=True) for item in items])

                # Add to general description
                if text and len(text) > 20:
                    description_parts.append(text)

        detail['description'] = '\n\n'.join(description_parts) if description_parts else ""
        detail['responsibilities'] = '\n'.join(responsibilities) if responsibilities else ""
        detail['qualifications'] = '\n'.join(qualifications) if qualifications else ""

        # Extract metadata fields
        # Look for job details table or metadata section
        metadata_section = html.select_one('.job-details, .vacancy-details, .field-group-div')
        if metadata_section:
            fields = metadata_section.find_all(['div', 'span', 'p', 'tr'])
            for field in fields:
                field_text = field.get_text(strip=True)
                field_lower = field_text.lower()

                # Extract grade/level
                if 'grade' in field_lower or 'level' in field_lower:
                    grade_match = re.search(r'(P-\d+|G-\d+|D-\d+|NO-[A-Z]|FS-\d+|L-\d+)', field_text, re.IGNORECASE)
                    if grade_match:
                        detail['grade'] = grade_match.group(1).upper()

                # Extract contract type
                if 'contract' in field_lower or 'appointment' in field_lower:
                    for contract_type in ['Fixed-term', 'Temporary', 'Continuing', 'Permanent', 'Consultant', 'Individual Contractor']:
                        if contract_type.lower() in field_lower:
                            detail['contract_type'] = contract_type
                            break

                # Extract organization
                if 'organization' in field_lower or 'department' in field_lower:
                    org_match = re.search(r':\s*(.+)$', field_text)
                    if org_match:
                        detail['organization'] = org_match.group(1).strip()

                # Extract location/duty station
                if 'duty station' in field_lower or 'location' in field_lower:
                    loc_match = re.search(r':\s*(.+)$', field_text)
                    if loc_match:
                        detail['location'] = loc_match.group(1).strip()

                # Extract deadline
                if 'deadline' in field_lower or 'closing date' in field_lower:
                    date_match = re.search(r'\d{1,2}[-/]\w{3,}[-/]\d{2,4}', field_text)
                    if date_match:
                        detail['deadline'] = date_match.group(0)

        # Extract education level
        qual_text = detail.get('qualifications', '') + detail.get('description', '')
        qual_lower = qual_text.lower()
        if 'advanced university degree' in qual_lower or "master's degree" in qual_lower or 'master' in qual_lower:
            detail['education_level'] = "Master's Degree"
        elif 'phd' in qual_lower or 'doctorate' in qual_lower:
            detail['education_level'] = "Doctorate"
        elif 'first-level university degree' in qual_lower or "bachelor's degree" in qual_lower or 'bachelor' in qual_lower:
            detail['education_level'] = "Bachelor's Degree"

        # Extract years of experience
        exp_match = re.search(r'(\d+)\s*(?:years?|yrs?)\s*of\s*(?:relevant\s*)?(?:professional\s*)?experience', qual_lower)
        if exp_match:
            detail['years_of_experience'] = int(exp_match.group(1))

        # Extract language requirements
        lang_requirements = {}
        lang_keywords = {
            'english': 'en',
            'french': 'fr',
            'spanish': 'es',
            'arabic': 'ar',
            'chinese': 'zh',
            'russian': 'ru'
        }

        for lang, code in lang_keywords.items():
            if lang in qual_lower:
                if f'{lang} is required' in qual_lower or f'{lang}: required' in qual_lower:
                    lang_requirements[code] = 'required'
                elif f'{lang} is desirable' in qual_lower or f'{lang}: desirable' in qual_lower:
                    lang_requirements[code] = 'desirable'

        if lang_requirements:
            detail['language_requirements'] = lang_requirements

        return detail

    def crawl(self, max_jobs: int = 100, language: str = "en") -> Dict:
        """Crawl UN Careers official website for job listings.

        Args:
            max_jobs: Maximum number of jobs to crawl
            language: Language code (en, fr, es, etc.)

        Returns:
            Dictionary with crawl statistics
        """
        jobs_data = []
        url = f"{self.job_opening_url}?language={language}"

        print(f"Crawling UN Careers: {url}")

        try:
            html = self.read_page(url)
            if not html:
                print("Failed to fetch job listing page")
                return self._create_result(jobs_data)

            # Find job listings
            # UN Careers typically uses a list or table structure
            job_elements = html.select('.view-content tr, .vacancy-list-item, .job-item')

            if not job_elements:
                # Try alternative selectors
                job_elements = html.select('tbody tr')

            print(f"Found {len(job_elements)} job elements")

            for idx, job_elem in enumerate(job_elements[:max_jobs]):
                try:
                    job_data = self.parse_job_element(job_elem)
                    if job_data:
                        # Fetch detailed information
                        if 'apply_url' in job_data and job_data['apply_url']:
                            print(f"Fetching details for: {job_data.get('title', 'Unknown')}")
                            detail = self.fetch_job_detail(job_data['apply_url'])
                            job_data.update(detail)

                        jobs_data.append(job_data)
                        print(f"  [{idx + 1}] {job_data.get('title', 'Unknown')} - {job_data.get('location', 'N/A')}")

                        # Rate limiting
                        time.sleep(1)

                except Exception as e:
                    print(f"Error parsing job element: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue

        except Exception as e:
            print(f"Error crawling UN Careers: {str(e)}")
            import traceback
            traceback.print_exc()

        # Save jobs to database
        saved_count = self.save_jobs(jobs_data) if jobs_data else 0

        return self._create_result(jobs_data, saved_count)

    def parse_job_element(self, element) -> Optional[Dict]:
        """Parse a single job listing element."""
        # Extract link
        link_elem = element.select_one('a[href*="jobopening"], a[href*="/lbw/"]')
        if not link_elem:
            return None

        href = link_elem.get('href', '')
        if href.startswith('/'):
            apply_url = f"{self.base_url}{href}"
        elif href.startswith('http'):
            apply_url = href
        else:
            apply_url = f"{self.base_url}/{href}"

        # Extract job ID from URL
        job_id_match = re.search(r'jobopening/(\d+)', apply_url)
        if job_id_match:
            job_id = f"UN-{job_id_match.group(1)}"
        else:
            job_id = f"UN-{href.split('/')[-1]}"

        # Extract basic fields from table cells or list items
        cells = element.find_all('td')

        job_data = {
            'job_id': job_id,
            'apply_url': apply_url,
            'source_url': self.job_opening_url,
            'organization': 'UN',
            'is_active': True,
            'posted_date': datetime.utcnow().date(),
        }

        # Parse table row format (typical UN Careers layout)
        if cells:
            # Title is usually in first or second cell
            for cell in cells:
                title_link = cell.select_one('a')
                if title_link:
                    job_data['title'] = title_link.get_text(strip=True)
                    break

            # Other fields from remaining cells
            for idx, cell in enumerate(cells):
                text = cell.get_text(strip=True)
                text_lower = text.lower()

                # Skip if it's the title cell
                if text == job_data.get('title'):
                    continue

                # Try to identify field type
                if re.match(r'^[A-Z]{2,}$', text):  # Organization code (e.g., UNDP, UNICEF)
                    job_data['organization'] = text
                elif re.search(r'P-\d+|G-\d+|D-\d+', text):  # Grade
                    job_data['grade'] = text
                elif ',' in text and len(text) < 100:  # Likely a location
                    job_data['location'] = text
                elif re.search(r'\d{1,2}[-/]\w{3,}[-/]\d{2,4}', text):  # Date
                    parsed_date = self.parse_date(text)
                    if parsed_date:
                        job_data['deadline'] = parsed_date.date()

        return job_data if job_data.get('title') else None

    def _create_result(self, jobs_data: List[Dict], saved_count: int = 0) -> Dict:
        """Create result dictionary."""
        return {
            "organization": "UN (careers.un.org)",
            "jobs_found": len(jobs_data),
            "jobs_saved": saved_count,
            "timestamp": datetime.utcnow().isoformat()
        }


def crawl_un_careers_official_sync(max_jobs: int = 100, language: str = "en"):
    """Synchronous wrapper for Celery task."""
    spider = UNCareersOfficialSpider()
    return spider.crawl(max_jobs=max_jobs, language=language)


def main():
    """Test the scraper."""
    spider = UNCareersOfficialSpider()
    result = spider.crawl(max_jobs=10)
    print("\n=== Crawl Results ===")
    print(f"Jobs found: {result['jobs_found']}")
    print(f"Jobs saved: {result['jobs_saved']}")
    print(f"Timestamp: {result['timestamp']}")


if __name__ == "__main__":
    main()
