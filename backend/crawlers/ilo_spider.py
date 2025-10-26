"""Crawler for ILO (International Labour Organization) careers."""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from crawlers.base_crawler import BaseCrawler
import time


class ILOSpider(BaseCrawler):
    """Spider for ILO careers website."""

    def __init__(self):
        super().__init__("ILO")
        self.base_url = "https://jobs.ilo.org"
        self.careers_url = f"{self.base_url}/vacancies"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
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

    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        text = text.strip()
        # Remove extra whitespace
        text = " ".join(text.split())
        return text

    def extract_experience(self, description: str) -> int:
        """Extract years of experience from description."""
        description_lower = description.lower()
        
        # Look for patterns like "5 years", "at least 3 years"
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'minimum\s*of\s*(\d+)\s*years?\s*experience',
            r'at\s*least\s*(\d+)\s*years?\s*experience',
            r'(\d+)\s*to\s*\d+\s*years?\s*experience',
        ]
        
        import re
        for pattern in patterns:
            match = re.search(pattern, description_lower)
            if match:
                return int(match.group(1))
        
        return 0

    def parse_job_detail(self, job_url: str) -> Dict:
        """Parse individual job detail page."""
        try:
            response = self.session.get(job_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job details
            title_elem = soup.find('h1')
            title = self.clean_text(title_elem.get_text()) if title_elem else ""
            
            # Extract description
            desc_elem = soup.find('div', class_='job-description') or soup.find('div', {'id': 'job-details'})
            description = ""
            if desc_elem:
                description = self.clean_text(desc_elem.get_text())
            else:
                # Try to get all paragraph content
                paragraphs = soup.find_all('p')
                description = "\n\n".join([self.clean_text(p.get_text()) for p in paragraphs if p.get_text().strip()])
            
            # Extract other details
            requirements = ""
            education = ""
            location = ""
            
            # Look for common patterns
            for elem in soup.find_all(['div', 'section', 'article']):
                class_name = elem.get('class', [])
                text_content = self.clean_text(elem.get_text())
                
                if any(keyword in text_content.lower() for keyword in ['requirements', 'qualifications']):
                    requirements = text_content
                
                if any(keyword in text_content.lower() for keyword in ['education', 'degree', 'university']):
                    education = text_content
                
                if any(keyword in text_content.lower() for keyword in ['location', 'duty station', 'office']):
                    location = text_content
            
            # Extract application deadline
            deadline = None
            deadline_patterns = [
                soup.find(text=lambda x: x and 'closing' in x.lower() and 'date' in x.lower()),
                soup.find(text=lambda x: x and 'deadline' in x.lower()),
            ]
            
            for pattern in deadline_patterns:
                if pattern:
                    # Try to extract date from surrounding text
                    parent = pattern.parent if hasattr(pattern, 'parent') else None
                    if parent:
                        deadline_text = self.clean_text(parent.get_text())
                        deadline = self.parse_date(deadline_text)
                        if deadline:
                            break
            
            return {
                "title": title,
                "description": description,
                "requirements": requirements,
                "education": education,
                "location": location,
                "deadline": deadline,
            }
        
        except Exception as e:
            print(f"  解析职位详情失败 {job_url}: {str(e)}")
            return {}

    def crawl(self) -> Dict:
        """Crawl ILO jobs."""
        print(f"\n开始爬取 ILO 职位...")
        
        all_jobs = []
        page = 1
        max_pages = 10  # Limit pages to avoid too many requests
        
        try:
            while page <= max_pages:
                print(f"\n爬取第 {page} 页...")
                
                url = f"{self.careers_url}?page={page}"
                response = self.session.get(url, timeout=30)
                
                if response.status_code != 200:
                    print(f"  获取页面失败，状态码: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings
                job_items = soup.find_all(['div', 'article', 'tr'], class_=lambda x: x and ('job' in x.lower() or 'vacancy' in x.lower() or 'listing' in x.lower()))
                
                if not job_items:
                    # Try alternative selector
                    job_items = soup.find_all('a', href=lambda x: x and '/vacancies/' in x or '/jobs/' in x)
                
                if not job_items:
                    print(f"  未找到职位，停止爬取")
                    break
                
                print(f"  找到 {len(job_items)} 个职位")
                
                for job_item in job_items:
                    try:
                        # Extract job link
                        link_elem = job_item if job_item.name == 'a' else job_item.find('a', href=True)
                        if not link_elem or not link_elem.get('href'):
                            continue
                        
                        job_path = link_elem.get('href')
                        if not job_path.startswith('http'):
                            job_path = f"{self.base_url}{job_path}"
                        
                        # Extract title
                        title_elem = link_elem if link_elem.name != 'a' else link_elem
                        title = self.clean_text(title_elem.get_text())
                        
                        if not title:
                            # Try to find title in the item
                            title_elem = job_item.find(['h2', 'h3', 'h4', 'strong', 'b'])
                            title = self.clean_text(title_elem.get_text()) if title_elem else ""
                        
                        # Extract basic info
                        org = "ILO"
                        
                        # Generate job_id
                        import hashlib
                        job_id = hashlib.md5(f"{org}_{title}_{job_path}".encode()).hexdigest()
                        
                        # Basic job data
                        job_data = {
                            "job_id": job_id,
                            "title": title,
                            "organization": org,
                            "url": job_path,
                            "location": "Not specified",
                            "contract_type": "Full-time",
                            "date_posted": datetime.utcnow(),
                            "last_scraped": datetime.utcnow(),
                        }
                        
                        # Try to get more details from detail page
                        detail_info = self.parse_job_detail(job_path)
                        if detail_info:
                            job_data.update(detail_info)
                        
                        # Extract experience from description
                        description = job_data.get("description", "")
                        job_data["experience_years"] = self.extract_experience(description)
                        
                        all_jobs.append(job_data)
                        print(f"  ✓ {title[:60]}...")
                        
                        time.sleep(0.5)  # Be polite to server
                        
                    except Exception as e:
                        print(f"  处理职位失败: {str(e)}")
                        continue
                
                # Check if there are more pages
                next_page = soup.find('a', text=lambda x: x and ('next' in x.lower() or '>' in x))
                if not next_page:
                    break
                
                page += 1
                time.sleep(1)  # Be polite between pages
            
        except Exception as e:
            print(f"爬取失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"\n总共爬取 {len(all_jobs)} 个职位")
        
        # Save to database
        if all_jobs:
            saved_count = self.save_jobs(all_jobs)
            return {
                "status": "success",
                "organization": "ILO",
                "total": len(all_jobs),
                "saved": saved_count
            }
        
        return {
            "status": "no_jobs",
            "organization": "ILO",
            "total": 0
        }


def crawl_ilo_sync(max_jobs: int = 50):
    """Synchronous wrapper for ILO crawler."""
    spider = ILOSpider()
    return spider.crawl(max_jobs=max_jobs)


if __name__ == "__main__":
    result = crawl_ilo_sync(max_jobs=20)
    print(f"ILO Crawler Result: {result}")

