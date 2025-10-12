"""Crawler for uncareer.net internships and jobs."""
import requests
import bs4
import re
from datetime import datetime
from typing import List, Dict, Optional
from crawlers.base_crawler import BaseCrawler


class UncareerSpider(BaseCrawler):
    """Spider for uncareer.net website."""

    def __init__(self):
        super().__init__("UN")
        self.base_url = "https://uncareer.net"

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object.

        Expected format: "DD Month YYYY" (e.g., "25 December 2025")
        """
        date_pattern = r"(\d{2}\s\w+\s\d{4})"
        matches = re.findall(date_pattern, date_str)
        if len(matches) == 0:
            return None

        date_string = matches[0]
        date_format = "%d %B %Y"
        try:
            return datetime.strptime(date_string, date_format)
        except ValueError:
            return None

    def read_page(self, url: str) -> bs4.BeautifulSoup:
        """Fetch and parse HTML page."""
        response = requests.get(url, timeout=30)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        return soup

    def fetch_detail(self, url: str) -> Dict:
        """Fetch job detail page and extract information."""
        html = self.read_page(url)

        # Extract title
        title_elem = html.find("h1")
        title = title_elem.text.strip() if title_elem else ""

        # Extract location and apply link
        list_groups = html.find_all('ul', class_='list-group')
        apply_link_button = html.select_one('.btn.btn-success[target="_blank"]')
        apply_link = ""
        if apply_link_button:
            apply_link = apply_link_button.get('href', '')

        country = ""
        city = ""
        organization = ""
        description = ""

        # Extract location details
        if len(list_groups) >= 2:
            group = list_groups[1]
            group_items = group.find_all('li')
            if len(group_items) > 2:
                country_elem = group_items[2].find("a")
                country = country_elem.text if country_elem else ""
            if len(group_items) > 3:
                city_elem = group_items[3].find("a")
                city = city_elem.text if city_elem else ""

        # Extract organization from first list group
        if len(list_groups) >= 1:
            org_elem = list_groups[0].find('a')
            organization = org_elem.text if org_elem else ""

        # Extract description
        desc_elem = html.find('div', class_='vacancy-description')
        if desc_elem:
            description = desc_elem.get_text(strip=True, separator="\n")

        return {
            "title": title,
            "country": country,
            "city": city,
            "organization": organization,
            "apply_link": apply_link,
            "description": description,
        }

    def parse_elements(self, elements: List) -> List[Dict]:
        """Parse job listing elements into structured data."""
        items = []

        for element in elements:
            try:
                # Extract basic info from listing
                link_elem = element.find('a')
                if not link_elem:
                    continue

                link = self.base_url + link_elem.get('href', '')
                title = link_elem.text.strip()

                # Parse title for city (format: "Title, City")
                split_title = title.split(", ")
                desc = ", ".join(split_title[:-1]) if len(split_title) > 1 else title
                city = split_title[-1] if len(split_title) > 1 else ""

                # Extract dates and organization
                p_elements = element.find_all('p')
                start_date_str = ""
                end_date_str = ""
                organization = ""

                if len(p_elements) >= 1:
                    org_elem = p_elements[0].find('a')
                    organization = org_elem.text if org_elem else ""

                if len(p_elements) >= 2:
                    start_date_str = p_elements[1].text

                if len(p_elements) >= 3:
                    end_date_str = p_elements[2].text

                # Fetch detailed information
                detail = self.fetch_detail(link)

                # Create job data matching Job model structure
                job_data = {
                    'job_id': f"UNCAREER-{link.split('/')[-1]}",
                    'title': detail['title'] or title,
                    'organization': detail['organization'] or organization,
                    'location': f"{detail['city']}, {detail['country']}" if detail['city'] and detail['country'] else city,
                    'description': detail['description'] or desc,
                    'apply_url': detail['apply_link'] if detail['apply_link'] else link,
                    'source_url': link,
                    'posted_date': self.parse_date(start_date_str).date() if self.parse_date(start_date_str) else datetime.utcnow().date(),
                    'deadline': self.parse_date(end_date_str).date() if self.parse_date(end_date_str) else None,
                    'is_active': True,
                }

                items.append(job_data)
                print(f"Parsed: {job_data['title']}")

            except Exception as e:
                print(f"Error parsing element: {str(e)}")
                continue

        return items

    def crawl(self, max_pages: int = 50, tag: str = "internship") -> Dict:
        """Crawl uncareer.net for job listings.

        Args:
            max_pages: Maximum number of pages to crawl
            tag: Tag to filter jobs (e.g., 'internship', 'job')

        Returns:
            Dictionary with crawl statistics
        """
        base_url = f'{self.base_url}/tag/{tag}'
        page = 1
        items_all = []

        while page <= max_pages:
            try:
                cur_url = f'{base_url}?page={page}'
                print(f'Fetching page {page}: {cur_url}')

                html = self.read_page(url=cur_url)
                elements = html.find_all('div', class_='vacancy')

                # Stop if no more jobs found
                if len(elements) == 0:
                    print(f"No more jobs found at page {page}")
                    break

                # Parse jobs from this page
                items = self.parse_elements(elements)
                items_all.extend(items)

                print(f"Found {len(items)} jobs on page {page}")
                page += 1

            except Exception as e:
                print(f"Error crawling page {page}: {str(e)}")
                break

        # Save jobs to database
        saved_count = self.save_jobs(items_all)

        return {
            "organization": "UNCareer.net",
            "tag": tag,
            "pages_crawled": page - 1,
            "jobs_found": len(items_all),
            "jobs_saved": saved_count,
            "timestamp": datetime.utcnow().isoformat()
        }


def crawl_uncareer_sync(max_pages: int = 50, tag: str = "internship"):
    """Synchronous wrapper for Celery task."""
    spider = UncareerSpider()
    return spider.crawl(max_pages=max_pages, tag=tag)


def main():
    """Test the scraper."""
    spider = UncareerSpider()
    result = spider.crawl(max_pages=1, tag="internship")
    print("\n=== Crawl Results ===")
    print(f"Pages crawled: {result['pages_crawled']}")
    print(f"Jobs found: {result['jobs_found']}")
    print(f"Jobs saved: {result['jobs_saved']}")


if __name__ == "__main__":
    main()
