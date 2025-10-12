"""Crawl jobs (not internships) to get different data."""
from crawlers.uncareer_spider import UncareerSpider

print("开始爬取正式职位...")
print("=" * 50)

spider = UncareerSpider()

# Crawl jobs (not internships)
print("\n正在爬取正式职位 (tag=job)...")
result = spider.crawl(max_pages=2, tag="job")

print("\n" + "=" * 50)
print(f"找到: {result['jobs_found']} 个职位")
print(f"保存: {result['jobs_saved']} 个新职位到数据库")
print("=" * 50)
