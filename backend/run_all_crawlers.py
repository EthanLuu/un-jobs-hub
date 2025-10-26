"""Run all available crawlers to update job data."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawlers.uncareer_spider import crawl_uncareer_sync
from crawlers.un_careers_official_spider import crawl_un_careers_official_sync
from crawlers.who_spider import crawl_who_sync
from crawlers.fao_spider import crawl_fao_sync
from crawlers.unops_spider import crawl_unops_sync
from crawlers.ilo_spider import crawl_ilo_sync


def main():
    """Run all crawlers and display results."""
    print("=" * 60)
    print("开始运行所有爬虫...")
    print("=" * 60)

    results = []

    # 1. UNCareer - Internships
    print("\n[1/7] 正在爬取 UNCareer.net - 实习职位...")
    print("-" * 60)
    try:
        result1 = crawl_uncareer_sync(max_pages=10, tag="internship")
        print(f"✓ 完成: 爬取 {result1['pages_crawled']} 页, 发现 {result1['jobs_found']} 个职位, 保存 {result1['jobs_saved']} 个")
        results.append(result1)
    except Exception as e:
        print(f"✗ 失败: {str(e)}")
        results.append({'jobs_found': 0, 'jobs_saved': 0})

    # 2. UNCareer - Jobs
    print("\n[2/7] 正在爬取 UNCareer.net - 正式职位...")
    print("-" * 60)
    try:
        result2 = crawl_uncareer_sync(max_pages=10, tag="job")
        print(f"✓ 完成: 爬取 {result2['pages_crawled']} 页, 发现 {result2['jobs_found']} 个职位, 保存 {result2['jobs_saved']} 个")
        results.append(result2)
    except Exception as e:
        print(f"✗ 失败: {str(e)}")
        results.append({'jobs_found': 0, 'jobs_saved': 0})

    # 3. UNCareer - Vacancies
    print("\n[3/7] 正在爬取 UNCareer.net - 空缺职位...")
    print("-" * 60)
    try:
        result3 = crawl_uncareer_sync(max_pages=10, tag="vacancy")
        print(f"✓ 完成: 爬取 {result3['pages_crawled']} 页, 发现 {result3['jobs_found']} 个职位, 保存 {result3['jobs_saved']} 个")
        results.append(result3)
    except Exception as e:
        print(f"✗ 失败: {str(e)}")
        results.append({'jobs_found': 0, 'jobs_saved': 0})

    # 4. UN Careers Official (careers.un.org)
    print("\n[4/7] 正在爬取 UN Careers 官方网站...")
    print("-" * 60)
    print("注意: 该网站可能有反爬虫保护")
    try:
        result4 = crawl_un_careers_official_sync(max_jobs=20, language="en")
        print(f"✓ 完成: 发现 {result4['jobs_found']} 个职位, 保存 {result4['jobs_saved']} 个")
        results.append(result4)
    except Exception as e:
        print(f"✗ 失败: {str(e)}")
        results.append({'jobs_found': 0, 'jobs_saved': 0})

    # 5. WHO (World Health Organization)
    print("\n[5/7] 正在爬取 WHO 世界卫生组织...")
    print("-" * 60)
    try:
        result5 = crawl_who_sync(max_jobs=20)
        print(f"✓ 完成: 发现 {result5['jobs_found']} 个职位, 保存 {result5['jobs_saved']} 个")
        results.append(result5)
    except Exception as e:
        print(f"✗ 失败: {str(e)}")
        results.append({'jobs_found': 0, 'jobs_saved': 0})

    # 6. FAO (Food and Agriculture Organization)
    print("\n[6/7] 正在爬取 FAO 联合国粮农组织...")
    print("-" * 60)
    try:
        result6 = crawl_fao_sync(max_jobs=20)
        print(f"✓ 完成: 发现 {result6['jobs_found']} 个职位, 保存 {result6['jobs_saved']} 个")
        results.append(result6)
    except Exception as e:
        print(f"✗ 失败: {str(e)}")
        results.append({'jobs_found': 0, 'jobs_saved': 0})

    # 7. UNOPS (United Nations Office for Project Services)
    print("\n[7/8] 正在爬取 UNOPS 联合国项目事务厅...")
    print("-" * 60)
    try:
        result7 = crawl_unops_sync(max_jobs=20)
        print(f"✓ 完成: 发现 {result7['jobs_found']} 个职位, 保存 {result7['jobs_saved']} 个")
        results.append(result7)
    except Exception as e:
        print(f"✗ 失败: {str(e)}")
        results.append({'jobs_found': 0, 'jobs_saved': 0})

    # 8. ILO (International Labour Organization)
    print("\n[8/8] 正在爬取 ILO 国际劳工组织...")
    print("-" * 60)
    try:
        result8 = crawl_ilo_sync(max_jobs=20)
        print(f"✓ 完成: 发现 {result8.get('total', 0)} 个职位, 保存 {result8.get('saved', 0)} 个")
        results.append({'jobs_found': result8.get('total', 0), 'jobs_saved': result8.get('saved', 0)})
    except Exception as e:
        print(f"✗ 失败: {str(e)}")
        results.append({'jobs_found': 0, 'jobs_saved': 0})

    # 总结
    total_found = sum(r.get('jobs_found', 0) for r in results)
    total_saved = sum(r.get('jobs_saved', 0) for r in results)

    print("\n" + "=" * 60)
    print("爬取完成!")
    print("=" * 60)
    print(f"总计发现: {total_found} 个职位")
    print(f"总计保存: {total_saved} 个职位")
    print("\n支持的联合国组织:")
    print("• UN Careers (careers.un.org)")
    print("• UNCareer.net (实习、正式、空缺职位)")
    print("• WHO (世界卫生组织)")
    print("• FAO (联合国粮农组织)")
    print("• UNOPS (联合国项目事务厅)")
    print("• ILO (国际劳工组织) - 新增")
    print("• UNDP (开发计划署) - 待完善")
    print("• UNICEF (儿童基金会) - 待完善")
    print("=" * 60)


if __name__ == "__main__":
    main()
