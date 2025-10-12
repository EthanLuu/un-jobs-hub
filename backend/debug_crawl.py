"""Debug script to test saving jobs."""
from crawlers.uncareer_spider import UncareerSpider
import traceback

print("测试爬虫和数据库保存...")
print("=" * 50)

spider = UncareerSpider()

try:
    print("\n正在测试数据库连接...")
    session = spider.SessionLocal()
    print("✓ 数据库连接成功")
    session.close()

    print("\n正在爬取第1页...")
    result = spider.crawl(max_pages=1, tag="internship")

    print("\n结果:")
    print(f"  找到: {result['jobs_found']} 个职位")
    print(f"  保存: {result['jobs_saved']} 个")

except Exception as e:
    print(f"\n错误: {str(e)}")
    traceback.print_exc()
