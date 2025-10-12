"""Quick script to crawl just 1 page for testing."""
from crawlers.uncareer_spider import UncareerSpider

print("开始快速爬取测试...")
print("=" * 50)

spider = UncareerSpider()

# Just crawl 1 page of internships
print("\n正在爬取第1页实习职位...")
result = spider.crawl(max_pages=1, tag="internship")

print("\n" + "=" * 50)
print("爬取结果:")
print(f"  找到: {result['jobs_found']} 个职位")
print(f"  保存: {result['jobs_saved']} 个到数据库")
print("=" * 50)
