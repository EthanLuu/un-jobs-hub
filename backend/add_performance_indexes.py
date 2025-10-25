"""Add performance indexes to improve query speed."""
import asyncio
from sqlalchemy import text
from database import get_async_session


async def add_performance_indexes():
    """Add indexes to improve query performance."""
    async with get_async_session() as session:
        try:
            # Add composite indexes for common query patterns
            indexes = [
                # Common filter combinations
                "CREATE INDEX IF NOT EXISTS idx_jobs_org_category ON jobs(organization, category)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_org_grade ON jobs(organization, grade)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_org_location ON jobs(organization, location)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_category_grade ON jobs(category, grade)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_contract_grade ON jobs(contract_type, grade)",
                
                # Date-based queries
                "CREATE INDEX IF NOT EXISTS idx_jobs_deadline_active ON jobs(deadline, is_active)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_posted_active ON jobs(posted_date, is_active)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_created_active ON jobs(created_at, is_active)",
                
                # Experience and education queries
                "CREATE INDEX IF NOT EXISTS idx_jobs_exp_edu ON jobs(years_of_experience, education_level)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_edu_grade ON jobs(education_level, grade)",
                
                # Full-text search indexes (if supported)
                "CREATE INDEX IF NOT EXISTS idx_jobs_title_gin ON jobs USING gin(to_tsvector('english', title))",
                "CREATE INDEX IF NOT EXISTS idx_jobs_description_gin ON jobs USING gin(to_tsvector('english', description))",
                
                # Status and organization queries
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_org ON jobs(is_active, organization)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_deadline ON jobs(is_active, deadline)",
            ]
            
            for index_sql in indexes:
                try:
                    await session.execute(text(index_sql))
                    print(f"✓ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    print(f"⚠️  Skipped index (may already exist or not supported): {e}")
            
            await session.commit()
            print("\n✅ Performance indexes added successfully!")
            
        except Exception as e:
            print(f"❌ Error adding indexes: {e}")
            await session.rollback()


async def analyze_query_performance():
    """Analyze query performance after adding indexes."""
    async with get_async_session() as session:
        try:
            # Test common queries
            queries = [
                "SELECT COUNT(*) FROM jobs WHERE is_active = true",
                "SELECT COUNT(*) FROM jobs WHERE organization = 'UN'",
                "SELECT COUNT(*) FROM jobs WHERE category = 'Programme Management'",
                "SELECT COUNT(*) FROM jobs WHERE grade LIKE 'P-%'",
                "SELECT COUNT(*) FROM jobs WHERE years_of_experience >= 5",
                "SELECT COUNT(*) FROM jobs WHERE deadline > CURRENT_DATE",
            ]
            
            print("\n📊 Query Performance Analysis:")
            print("-" * 50)
            
            for query in queries:
                start_time = asyncio.get_event_loop().time()
                result = await session.execute(text(query))
                count = result.scalar()
                end_time = asyncio.get_event_loop().time()
                
                duration = (end_time - start_time) * 1000  # Convert to milliseconds
                print(f"{query[:40]}... | {count:>6} results | {duration:>6.2f}ms")
            
        except Exception as e:
            print(f"❌ Error analyzing performance: {e}")


if __name__ == "__main__":
    async def main():
        print("🚀 Adding performance indexes to UN Jobs Hub database...")
        await add_performance_indexes()
        await analyze_query_performance()
    
    asyncio.run(main())
