"""Check database contents."""
import asyncio
from sqlalchemy import select, func
from database import AsyncSessionLocal
from models.job import Job


async def check_database():
    """Check what's in the database."""
    async with AsyncSessionLocal() as session:
        # Count total jobs
        result = await session.execute(select(func.count()).select_from(Job))
        total = result.scalar()

        print(f"数据库中的职位总数: {total}")

        # Get sample jobs
        result = await session.execute(
            select(Job).limit(5).order_by(Job.created_at.desc())
        )
        jobs = result.scalars().all()

        print(f"\n最新的 5 个职位:")
        print("=" * 80)
        for job in jobs:
            print(f"  标题: {job.title}")
            print(f"  机构: {job.organization}")
            print(f"  地点: {job.location}")
            print(f"  截止日期: {job.deadline}")
            print(f"  创建时间: {job.created_at}")
            print("-" * 80)

        # Get organization stats
        result = await session.execute(
            select(Job.organization, func.count(Job.id))
            .group_by(Job.organization)
        )
        org_stats = result.all()

        print(f"\n各机构职位统计:")
        print("=" * 50)
        for org, count in org_stats:
            print(f"  {org}: {count} 个职位")


if __name__ == "__main__":
    asyncio.run(check_database())
