"""快速性能优化脚本 - 创建必要的索引"""
import asyncio
from sqlalchemy import text
from database import get_async_session


async def add_essential_indexes():
    """添加最关键的索引以快速提升性能"""
    async with get_async_session() as session:
        try:
            print("🚀 开始添加关键性能索引...\n")
            
            # 最关键的索引 - 这些会带来最大的性能提升
            essential_indexes = [
                # 最重要的复合索引 - is_active 是所有查询的基本过滤条件
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_created ON jobs(is_active, created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_deadline ON jobs(is_active, deadline DESC)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_org ON jobs(is_active, organization)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_category ON jobs(is_active, category)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_grade ON jobs(is_active, grade)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_location ON jobs(is_active, location)",
                
                # 单独的 is_active 索引（如果查询只过滤 is_active）
                "CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active)",
            ]
            
            created_count = 0
            skipped_count = 0
            
            for index_sql in essential_indexes:
                try:
                    await session.execute(text(index_sql))
                    index_name = index_sql.split('idx_')[1].split(' ')[0]
                    print(f"✅ 创建索引: {index_name}")
                    created_count += 1
                except Exception as e:
                    index_name = index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else "未知"
                    print(f"⚠️  跳过索引 {index_name}: {e}")
                    skipped_count += 1
            
            await session.commit()
            
            # 分析表以更新统计信息
            print("\n📊 分析表以优化查询计划...")
            await session.execute(text("ANALYZE jobs"))
            await session.commit()
            
            print(f"\n✅ 完成！")
            print(f"   - 创建了 {created_count} 个索引")
            if skipped_count > 0:
                print(f"   - 跳过了 {skipped_count} 个索引（可能已存在或不支持）")
            
            # 测试查询性能
            print("\n🧪 测试查询性能...")
            await test_query_performance(session)
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            await session.rollback()


async def test_query_performance(session):
    """测试常见查询的性能"""
    queries = [
        ("基础列表查询", "SELECT COUNT(*) FROM jobs WHERE is_active = true"),
        ("带组织过滤", "SELECT COUNT(*) FROM jobs WHERE is_active = true AND organization = (SELECT organization FROM jobs WHERE is_active = true LIMIT 1)"),
    ]
    
    for name, query in queries:
        import time
        start = time.time()
        result = await session.execute(text(query))
        count = result.scalar()
        duration = (time.time() - start) * 1000
        print(f"   {name}: {count} 条结果 | {duration:.2f}ms")


if __name__ == "__main__":
    print("=" * 60)
    print("UN Jobs Hub - 快速性能优化")
    print("=" * 60)
    print()
    asyncio.run(add_essential_indexes())
    print()
    print("💡 提示: 运行 'python add_performance_indexes.py' 添加完整索引集合")
