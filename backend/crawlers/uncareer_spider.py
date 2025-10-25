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
        """Fetch job detail page and extract comprehensive information."""
        html = self.read_page(url)

        # Extract title
        title_elem = html.find("h1")
        title = title_elem.text.strip() if title_elem else ""

        # Initialize all fields
        apply_link = ""
        country = ""
        city = ""
        organization = ""
        description = ""
        responsibilities = ""
        qualifications = ""
        grade = ""
        contract_type = ""
        category = ""
        education_level = ""
        years_of_experience = None
        language_requirements = {}

        # Extract apply link
        apply_link_button = html.select_one('.btn.btn-success[target="_blank"]')
        if apply_link_button:
            apply_link = apply_link_button.get('href', '')

        # Extract job details from list groups
        list_groups = html.find_all('ul', class_='list-group')

        # First list group contains dates (we'll use these for posted_date and deadline)
        # Second list group contains: Tags, Organization, Country, City, Post Level
        if len(list_groups) >= 2:
            group = list_groups[1]  # Second group has the metadata
            group_items = group.find_all('li')

            for item in group_items:
                item_text = item.get_text(strip=True)

                # Organization
                if item_text.startswith('Organization:'):
                    org_elem = item.find("a")
                    if org_elem:
                        organization = org_elem.text.strip()
                    else:
                        organization = item_text.replace('Organization:', '').strip()

                # Country
                elif item_text.startswith('Country:'):
                    country_elem = item.find("a")
                    if country_elem:
                        country = country_elem.text.strip()
                    else:
                        country = item_text.replace('Country:', '').strip()

                # City
                elif item_text.startswith('City:'):
                    city_elem = item.find("a")
                    if city_elem:
                        city = city_elem.text.strip()
                    else:
                        city = item_text.replace('City:', '').strip()

                # Post Level (this is the grade)
                elif item_text.startswith('Post Level:'):
                    post_level = item_text.replace('Post Level:', '').strip()
                    # Try to extract actual UN grade from post level
                    # Post level might be like "Chief and Senior Professional" or contain grade code
                    if post_level:
                        # Check if it contains a grade pattern
                        import re
                        grade_match = re.search(r'(P-\d+|G-\d+|D-\d+|NO-[A-Z]|FS-\d+|L-\d+|GS-\d+)', post_level, re.IGNORECASE)
                        if grade_match:
                            grade = grade_match.group(1).upper()
                        else:
                            # Store the post level text as category if no grade found
                            category = post_level

                # Tags (could be used for category)
                elif item_text.startswith('Tags:'):
                    if not category:  # Only if we haven't set category from Post Level
                        tags = item_text.replace('Tags:', '').strip()
                        # Take first tag as category
                        if tags:
                            tag_list = [t.strip() for t in tags.split() if t.strip()]
                            if tag_list:
                                category = tag_list[0]

        # Extract main job description
        # The actual description is in the first paragraph(s) of col-md-9
        main_content = html.find('div', class_='col-md-9')
        if main_content:
            # Get all paragraphs
            all_paragraphs = main_content.find_all('p')

            # Filter out promotional content (contains emoji or "Discover How" etc)
            actual_content_paras = []
            for p in all_paragraphs:
                text = p.get_text(strip=True)
                # Skip promotional paragraphs
                if any(keyword in text for keyword in ['📚', '⚠️', 'Discover How', 'Change Your Life', 'Recruitment Guide']):
                    continue
                if text and len(text) > 30:  # Meaningful content
                    actual_content_paras.append(text)

            # Combine actual content paragraphs
            if actual_content_paras:
                full_description = '\n\n'.join(actual_content_paras)
                description = full_description

                # Try to parse sections from description
                desc_lower = full_description.lower()

                # Split by common section markers
                sections = {}
                current_section = 'description'
                current_text = []

                for para in actual_content_paras:
                    para_lower = para.lower()

                    # Check for section headers (at the start of paragraph)
                    if any(keyword in para_lower[:60] for keyword in ['responsibilities:', 'duties and responsibilities', 'accountabilities:']):
                        if current_text:
                            sections[current_section] = '\n\n'.join(current_text)
                        current_section = 'responsibilities'
                        current_text = [para]
                    elif any(keyword in para_lower[:60] for keyword in ['qualifications/special skills', 'qualifications:', 'requirements:', 'competencies:', 'education:']):
                        if current_text:
                            sections[current_section] = '\n\n'.join(current_text)
                        current_section = 'qualifications'
                        current_text = [para]
                    else:
                        current_text.append(para)

                # Save last section
                if current_text:
                    sections[current_section] = '\n\n'.join(current_text)

                # Extract to fields
                if 'responsibilities' in sections:
                    responsibilities = sections['responsibilities']
                if 'qualifications' in sections:
                    qualifications = sections['qualifications']

                # If we didn't find sections with headers, try to extract from full description
                if not responsibilities or not qualifications:
                    # Look for "Duties and Responsibilities" section
                    resp_match = desc_lower.find('duties and responsibilities')
                    qual_match = desc_lower.find('qualifications/special skills')

                    if resp_match != -1 and qual_match != -1 and resp_match < qual_match:
                        # Extract text between these markers
                        responsibilities = full_description[resp_match:qual_match].strip()
                        qualifications = full_description[qual_match:].strip()

                        # Clean up language section if present
                        lang_match = qualifications.lower().find('languages')
                        if lang_match != -1:
                            # Find next section after languages
                            additional_match = qualifications.lower().find('additional information', lang_match)
                            if additional_match != -1:
                                qualifications = qualifications[:additional_match].strip()

                # Try to extract education level from qualifications or full description
                text_to_search = qualifications if qualifications else full_description
                if text_to_search:
                    text_lower = text_to_search.lower()
                    if 'master' in text_lower or 'advanced university degree' in text_lower:
                        education_level = "Master's Degree"
                    elif 'phd' in text_lower or 'doctorate' in text_lower:
                        education_level = "Doctorate"
                    elif 'bachelor' in text_lower:
                        education_level = "Bachelor's Degree"

                    # Try to extract years of experience
                    # Matches patterns like: "5 years", "(5) years", "five (5) years"
                    import re
                    exp_match = re.search(r'(\d+)\s*\)?\s*years?\s+(?:of\s+)?(?:relevant\s+)?(?:professional\s+)?(?:working\s+)?experience', text_lower)
                    if exp_match:
                        years_of_experience = int(exp_match.group(1))

                # Extract language requirements
                lang_keywords = {
                    'english': 'en',
                    'french': 'fr',
                    'spanish': 'es',
                    'arabic': 'ar',
                    'chinese': 'zh',
                    'russian': 'ru'
                }

                for lang, code in lang_keywords.items():
                    if lang in desc_lower:
                        if f'{lang} is required' in desc_lower or f'{lang}: required' in desc_lower or 'fluency in ' + lang in desc_lower:
                            language_requirements[code] = 'required'
                        elif f'{lang} is desirable' in desc_lower or f'{lang}: desirable' in desc_lower or 'knowledge of ' + lang in desc_lower:
                            language_requirements[code] = 'desirable'

        return {
            "title": title,
            "country": country,
            "city": city,
            "organization": organization,
            "apply_link": apply_link,
            "description": description,
            "responsibilities": responsibilities,
            "qualifications": qualifications,
            "grade": grade,
            "contract_type": contract_type,
            "category": category,
            "education_level": education_level,
            "years_of_experience": years_of_experience,
            "language_requirements": language_requirements,
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
                    'duty_station': detail['city'] or city,
                    'description': detail['description'] or desc,
                    'responsibilities': detail['responsibilities'] if detail['responsibilities'] else None,
                    'qualifications': detail['qualifications'] if detail['qualifications'] else None,
                    'grade': detail['grade'] if detail['grade'] else None,
                    'contract_type': detail['contract_type'] if detail['contract_type'] else None,
                    'category': detail['category'] if detail['category'] else None,
                    'education_level': detail['education_level'] if detail['education_level'] else None,
                    'years_of_experience': detail['years_of_experience'],
                    'language_requirements': detail['language_requirements'] if detail['language_requirements'] else None,
                    'apply_url': detail['apply_link'] if detail['apply_link'] else link,
                    'source_url': link,
                    'posted_date': self.parse_date(start_date_str).date() if self.parse_date(start_date_str) else datetime.utcnow().date(),
                    'deadline': self.parse_date(end_date_str).date() if self.parse_date(end_date_str) else None,
                    'is_active': True,
                }

                items.append(job_data)
                print(f"Parsed: {job_data['title']} ({job_data['organization']}) - {job_data['grade'] or 'N/A'}")

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
