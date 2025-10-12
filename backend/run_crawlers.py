"""Script to run all crawlers and populate database with real job data."""
import asyncio
from crawlers.uncareer_spider import UncareerSpider


def run_all_crawlers():
    """Run all available crawlers."""
    print("=" * 50)
    print("开始运行爬虫...")
    print("=" * 50)

    # Run UnCareer spider (synchronous)
    print(f"\n{'=' * 50}")
    print("正在爬取: UNCareer.net")
    print(f"{'=' * 50}")

    try:
        spider = UncareerSpider()
        # Crawl both internships and jobs, limit to 2 pages each for faster testing
        result1 = spider.crawl(max_pages=3, tag="internship")
        print(f"\n✓ UNCareer (实习): 找到 {result1['jobs_found']} 个职位, 保存了 {result1['jobs_saved']} 个")

        result2 = spider.crawl(max_pages=3, tag="job")
        print(f"✓ UNCareer (职位): 找到 {result2['jobs_found']} 个职位, 保存了 {result2['jobs_saved']} 个")

        total_saved = result1['jobs_saved'] + result2['jobs_saved']
        total_found = result1['jobs_found'] + result2['jobs_found']

        print(f"\n{'=' * 50}")
        print(f"爬虫运行完成!")
        print(f"总共找到 {total_found} 个职位")
        print(f"总共保存了 {total_saved} 个职位到数据库")
        print(f"{'=' * 50}")

    except Exception as e:
        print(f"✗ 爬取失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_crawlers()
