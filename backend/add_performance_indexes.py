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
                # Most critical: is_active is used in every query
                "CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active)",
                
                # Composite index for active jobs with sorting
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_created ON jobs(is_active, created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_deadline ON jobs(is_active, deadline DESC)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_posted ON jobs(is_active, posted_date DESC)",
                
                # Filter combinations with is_active (most common filters)
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_org ON jobs(is_active, organization)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_category ON jobs(is_active, category)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_grade ON jobs(is_active, grade)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_location ON jobs(is_active, location)",
                
                # Experience and education with is_active
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_exp ON jobs(is_active, years_of_experience)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_edu ON jobs(is_active, education_level)",
                
                # Multi-column filters (common combinations)
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_org_cat ON jobs(is_active, organization, category)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_org_grade ON jobs(is_active, organization, grade)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_active_cat_grade ON jobs(is_active, category, grade)",
                
                # Text search optimization
                # For ILIKE queries on location (prefix pattern only)
                "CREATE INDEX IF NOT EXISTS idx_jobs_location_trgm ON jobs USING gin(location gin_trgm_ops)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_title_trgm ON jobs USING gin(title gin_trgm_ops)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_org_trgm ON jobs USING gin(organization gin_trgm_ops)",
                
                # Full-text search indexes
                "CREATE INDEX IF NOT EXISTS idx_jobs_title_fts ON jobs USING gin(to_tsvector('english', title))",
                "CREATE INDEX IF NOT EXISTS idx_jobs_description_fts ON jobs USING gin(to_tsvector('english', description))",
            ]
            
            # Check if pg_trgm extension is available
            try:
                await session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
                print("✓ Created pg_trgm extension for fuzzy text search")
            except Exception as e:
                print(f"⚠️  pg_trgm extension not available: {e}")
            
            for index_sql in indexes:
                try:
                    await session.execute(text(index_sql))
                    print(f"✓ Created index: {index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else index_sql}")
                except Exception as e:
                    print(f"⚠️  Skipped index (may already exist or not supported): {e}")
            
            await session.commit()
            print("\n✅ Performance indexes added successfully!")
            
            # Analyze tables for better query planning
            await session.execute(text("ANALYZE jobs"))
            print("✓ Analyzed jobs table for query optimization")
            await session.commit()
            
        except Exception as e:
            print(f"❌ Error adding indexes: {e}")
            await session.rollback()


async def analyze_query_performance():
    """Analyze query performance after adding indexes."""
    async with get_async_session() as session:
        try:
            # Test common queries
            queries = [
                ("SELECT COUNT(*) FROM jobs WHERE is_active = true", "Basic active count"),
                ("SELECT COUNT(*) FROM jobs WHERE is_active = true AND organization = 'UNDP'", "With org filter"),
                ("SELECT COUNT(*) FROM jobs WHERE is_active = true AND category = 'Programme'", "With category"),
                ("SELECT COUNT(*) FROM jobs WHERE is_active = true AND grade LIKE 'P-%'", "With grade pattern"),
                ("SELECT COUNT(*) FROM jobs WHERE is_active = true AND years_of_experience >= 5", "With experience"),
                ("SELECT * FROM jobs WHERE is_active = true ORDER BY created_at DESC LIMIT 20", "Basic listing"),
            ]
            
            print("\n📊 Query Performance Analysis:")
            print("-" * 60)
            
            for query, description in queries:
                start_time = asyncio.get_event_loop().time()
                result = await session.execute(text(query))
                rows = result.fetchall()
                end_time = asyncio.get_event_loop().time()
                
                duration = (end_time - start_time) * 1000  # Convert to milliseconds
                row_count = len(rows)
                print(f"{description:.<40} {row_count:>6} rows | {duration:>7.2f}ms")
            
        except Exception as e:
            print(f"❌ Error analyzing performance: {e}")


async def get_index_usage_stats():
    """Get statistics about index usage."""
    async with get_async_session() as session:
        try:
            query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                WHERE tablename = 'jobs'
                ORDER BY idx_scan DESC
            """)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            print("\n📈 Index Usage Statistics:")
            print("-" * 80)
            print(f"{'Index Name':<40} {'Scans':<10} {'Tuples Read':<15}")
            print("-" * 80)
            
            for row in rows[:15]:  # Show top 15 indexes
                print(f"{row[2]:<40} {row[3]:<10} {row[4]:<15}")
                
        except Exception as e:
            print(f"⚠️  Could not get index stats: {e}")


if __name__ == "__main__":
    async def main():
        print("🚀 Adding performance indexes to UN Jobs Hub database...")
        await add_performance_indexes()
        await analyze_query_performance()
        await get_index_usage_stats()
    
    asyncio.run(main())
