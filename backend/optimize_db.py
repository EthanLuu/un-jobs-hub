#!/usr/bin/env python3
"""
Database optimization and analysis tool.

Provides utilities for:
- Query performance analysis
- Index optimization recommendations
- Table statistics
- Slow query identification
- Database health check
"""

import asyncio
from sqlalchemy import text
from database import get_async_session
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Database optimization and analysis tools."""

    async def analyze_table_sizes(self) -> List[Dict[str, Any]]:
        """Get table sizes and row counts."""
        async with get_async_session() as session:
            query = """
                SELECT
                    table_name,
                    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS total_size,
                    pg_size_pretty(pg_relation_size(quote_ident(table_name))) AS table_size,
                    pg_size_pretty(pg_total_relation_size(quote_ident(table_name)) -
                                   pg_relation_size(quote_ident(table_name))) AS indexes_size,
                    (SELECT count(*) FROM information_schema.columns
                     WHERE table_name = t.table_name) AS column_count
                FROM information_schema.tables t
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC;
            """
            result = await session.execute(text(query))
            return [dict(row._mapping) for row in result]

    async def analyze_indexes(self) -> List[Dict[str, Any]]:
        """Get index usage statistics."""
        async with get_async_session() as session:
            query = """
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan as scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched,
                    pg_size_pretty(pg_relation_size(indexrelid)) as size
                FROM pg_stat_user_indexes
                ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC;
            """
            result = await session.execute(text(query))
            return [dict(row._mapping) for row in result]

    async def find_missing_indexes(self) -> List[Dict[str, Any]]:
        """Suggest missing indexes based on query patterns."""
        async with get_async_session() as session:
            query = """
                SELECT
                    schemaname,
                    tablename,
                    attname as column_name,
                    n_distinct,
                    correlation
                FROM pg_stats
                WHERE schemaname = 'public'
                AND n_distinct > 100  -- High cardinality columns
                AND correlation < 0.5  -- Low correlation (random order)
                ORDER BY n_distinct DESC;
            """
            result = await session.execute(text(query))
            return [dict(row._mapping) for row in result]

    async def get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get slow query statistics (requires pg_stat_statements extension)."""
        async with get_async_session() as session:
            try:
                query = """
                    SELECT
                        query,
                        calls,
                        total_exec_time / 1000 as total_time_sec,
                        mean_exec_time / 1000 as mean_time_sec,
                        max_exec_time / 1000 as max_time_sec,
                        rows
                    FROM pg_stat_statements
                    WHERE query NOT LIKE '%pg_stat_statements%'
                    ORDER BY mean_exec_time DESC
                    LIMIT 10;
                """
                result = await session.execute(text(query))
                return [dict(row._mapping) for row in result]
            except Exception as e:
                logger.warning(f"pg_stat_statements not available: {e}")
                return []

    async def analyze_table_bloat(self) -> List[Dict[str, Any]]:
        """Detect table bloat (wasted space)."""
        async with get_async_session() as session:
            query = """
                SELECT
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                    CASE WHEN otta=0 OR sml.relpages=0 OR sml.relpages=otta THEN 0.0
                         ELSE round(((sml.relpages-otta)::numeric * 100/ sml.relpages)::numeric, 1)
                    END AS tbloat
                FROM (
                    SELECT
                        schemaname, tablename, cc.relpages, bs,
                        CEIL((cc.reltuples*((datahdr+ma-
                            (CASE WHEN datahdr%ma=0 THEN ma ELSE datahdr%ma END))+nullhdr2+4))/(bs-20::float)) AS otta
                    FROM (
                        SELECT
                            ma,bs,schemaname,tablename,
                            (datawidth+(hdr+ma-(case when hdr%ma=0 THEN ma ELSE hdr%ma END)))::numeric AS datahdr,
                            (maxfracsum*(nullhdr+ma-(case when nullhdr%ma=0 THEN ma ELSE nullhdr%ma END))) AS nullhdr2
                        FROM (
                            SELECT
                                schemaname, tablename, hdr, ma, bs,
                                SUM((1-null_frac)*avg_width) AS datawidth,
                                MAX(null_frac) AS maxfracsum,
                                hdr+(
                                    SELECT 1+count(*)/8
                                    FROM pg_stats s2
                                    WHERE null_frac<>0 AND s2.schemaname = s.schemaname AND s2.tablename = s.tablename
                                ) AS nullhdr
                            FROM pg_stats s, (
                                SELECT
                                    (SELECT current_setting('block_size')::numeric) AS bs,
                                    CASE WHEN substring(v,12,3) IN ('8.0','8.1','8.2') THEN 27 ELSE 23 END AS hdr,
                                    CASE WHEN v ~ 'mingw32' THEN 8 ELSE 4 END AS ma
                                FROM (SELECT version() AS v) AS foo
                            ) AS constants
                            WHERE schemaname='public'
                            GROUP BY 1,2,3,4,5
                        ) AS foo
                    ) AS rs
                    JOIN pg_class cc ON cc.relname = rs.tablename
                    JOIN pg_namespace nn ON cc.relnamespace = nn.oid AND nn.nspname = rs.schemaname AND nn.nspname <> 'information_schema'
                ) AS sml
                WHERE sml.relpages - otta > 0
                ORDER BY tbloat DESC;
            """
            try:
                result = await session.execute(text(query))
                return [dict(row._mapping) for row in result]
            except Exception as e:
                logger.warning(f"Bloat analysis failed: {e}")
                return []

    async def vacuum_analyze_all(self):
        """Run VACUUM ANALYZE on all tables."""
        async with get_async_session() as session:
            logger.info("Running VACUUM ANALYZE on all tables...")
            await session.execute(text("VACUUM ANALYZE;"))
            await session.commit()
            logger.info("VACUUM ANALYZE completed")

    async def get_database_stats(self) -> Dict[str, Any]:
        """Get overall database statistics."""
        async with get_async_session() as session:
            stats = {}

            # Database size
            result = await session.execute(text(
                "SELECT pg_size_pretty(pg_database_size(current_database())) as db_size;"
            ))
            stats['database_size'] = result.scalar()

            # Connection count
            result = await session.execute(text(
                "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database();"
            ))
            stats['active_connections'] = result.scalar()

            # Transaction stats
            result = await session.execute(text("""
                SELECT
                    xact_commit as commits,
                    xact_rollback as rollbacks,
                    blks_read as blocks_read,
                    blks_hit as blocks_hit,
                    tup_returned as tuples_returned,
                    tup_fetched as tuples_fetched,
                    tup_inserted as tuples_inserted,
                    tup_updated as tuples_updated,
                    tup_deleted as tuples_deleted
                FROM pg_stat_database
                WHERE datname = current_database();
            """))
            db_stats = result.first()
            if db_stats:
                stats.update(dict(db_stats._mapping))

            # Cache hit ratio
            if stats.get('blocks_hit') and stats.get('blocks_read'):
                total_reads = stats['blocks_hit'] + stats['blocks_read']
                stats['cache_hit_ratio'] = round(
                    (stats['blocks_hit'] / total_reads * 100) if total_reads > 0 else 0,
                    2
                )

            return stats

    async def generate_report(self):
        """Generate comprehensive database optimization report."""
        print("\n" + "=" * 80)
        print("DATABASE OPTIMIZATION REPORT")
        print("=" * 80)

        # Database stats
        print("\n📊 Database Statistics:")
        print("-" * 80)
        stats = await self.get_database_stats()
        for key, value in stats.items():
            print(f"  {key:25}: {value}")

        # Table sizes
        print("\n📦 Table Sizes:")
        print("-" * 80)
        tables = await self.analyze_table_sizes()
        for table in tables[:10]:  # Top 10
            print(f"  {table['table_name']:20} | "
                  f"Total: {table['total_size']:10} | "
                  f"Table: {table['table_size']:10} | "
                  f"Indexes: {table['indexes_size']:10}")

        # Index usage
        print("\n🔍 Index Usage (Unused/Rarely Used):")
        print("-" * 80)
        indexes = await self.analyze_indexes()
        unused = [idx for idx in indexes if idx['scans'] < 100]
        for idx in unused[:10]:
            print(f"  {idx['indexname']:30} on {idx['tablename']:15} | "
                  f"Scans: {idx['scans']:5} | Size: {idx['size']}")

        # Missing indexes
        print("\n⚠️  Potential Missing Indexes (High Cardinality Columns):")
        print("-" * 80)
        missing = await self.find_missing_indexes()
        for col in missing[:10]:
            print(f"  {col['tablename']:20}.{col['column_name']:25} | "
                  f"Distinct: {col['n_distinct']:10} | "
                  f"Correlation: {col['correlation']:.2f}")

        # Slow queries
        print("\n🐌 Slow Queries:")
        print("-" * 80)
        slow_queries = await self.get_slow_queries()
        if slow_queries:
            for i, query in enumerate(slow_queries[:5], 1):
                print(f"\n  Query {i}:")
                print(f"    Mean Time: {query['mean_time_sec']:.3f}s")
                print(f"    Max Time: {query['max_time_sec']:.3f}s")
                print(f"    Calls: {query['calls']}")
                print(f"    Query: {query['query'][:100]}...")
        else:
            print("  pg_stat_statements extension not available")

        # Table bloat
        print("\n💨 Table Bloat:")
        print("-" * 80)
        bloat = await self.analyze_table_bloat()
        if bloat:
            for table in bloat[:10]:
                if table['tbloat'] > 20:  # > 20% bloat
                    print(f"  {table['tablename']:20} | "
                          f"Size: {table['size']:10} | "
                          f"Bloat: {table['tbloat']}%")
        else:
            print("  Bloat analysis not available")

        print("\n" + "=" * 80)
        print("RECOMMENDATIONS:")
        print("=" * 80)
        print("1. Consider removing unused indexes to save space")
        print("2. Add indexes on high-cardinality, low-correlation columns")
        print("3. Run VACUUM ANALYZE regularly (run with --vacuum flag)")
        print("4. Monitor slow queries and optimize them")
        print("5. Consider partitioning large tables")
        print("=" * 80 + "\n")


async def main():
    """Main entry point."""
    import sys

    optimizer = DatabaseOptimizer()

    if '--vacuum' in sys.argv:
        await optimizer.vacuum_analyze_all()
    else:
        await optimizer.generate_report()


if __name__ == "__main__":
    asyncio.run(main())
