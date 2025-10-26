"""
Database initialization and seeding script.

Provides utilities for initializing the database and seeding data.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from database import get_engine, Base
from config import settings
import logging

logger = logging.getLogger(__name__)


async def create_database_if_not_exists():
    """Create database if it doesn't exist."""
    print("Checking if database exists...")

    # Parse database URL to get database name
    from urllib.parse import urlparse
    parsed = urlparse(settings.database_url)
    db_name = parsed.path.lstrip('/')

    if not db_name:
        print("⚠️  No database name specified in DATABASE_URL")
        return

    # Create connection to postgres database (not the target database)
    postgres_url = settings.database_url.rsplit('/', 1)[0] + '/postgres'

    try:
        engine = get_engine(database_url=postgres_url)
        async with engine.connect() as conn:
            # Check if database exists
            await conn.execute(text("COMMIT"))  # End any active transaction
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            )
            exists = result.scalar()

            if not exists:
                print(f"Creating database: {db_name}")
                await conn.execute(text("COMMIT"))
                await conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Database {db_name} created successfully!")
            else:
                print(f"✅ Database {db_name} already exists")

        await engine.dispose()
    except Exception as e:
        print(f"⚠️  Could not check/create database: {e}")
        print("This is normal if using a hosted database service")


async def create_tables():
    """Create all database tables."""
    print("Creating database tables...")

    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ All tables created successfully!")
        await engine.dispose()
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


async def drop_all_tables():
    """Drop all database tables (use with caution)."""
    print("⚠️  WARNING: This will drop all tables!")
    response = input("Are you sure? Type 'yes' to confirm: ")

    if response.lower() != 'yes':
        print("❌ Operation cancelled")
        return

    print("Dropping all tables...")

    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("✅ All tables dropped successfully!")
        await engine.dispose()
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        raise


async def check_database_connection():
    """Check if database connection works."""
    print("Testing database connection...")

    try:
        engine = get_engine()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
        print("✅ Database connection successful!")
        await engine.dispose()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def show_tables():
    """Show all tables in the database."""
    print("Listing database tables...")

    try:
        engine = get_engine()
        async with engine.connect() as conn:
            # PostgreSQL query to list tables
            result = await conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()

            if tables:
                print("\n📋 Tables:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("No tables found in database")

        await engine.dispose()
    except Exception as e:
        print(f"❌ Error listing tables: {e}")
        raise


async def seed_test_data():
    """Seed database with test data for development."""
    print("Seeding test data...")
    print("⚠️  This is for development only!")

    try:
        from models.user import User
        from utils.auth import get_password_hash
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker

        engine = get_engine()
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as session:
            # Create test admin user
            from sqlalchemy import select

            result = await session.execute(
                select(User).where(User.email == "admin@unjobshub.com")
            )
            admin_user = result.scalar_one_or_none()

            if not admin_user:
                admin_user = User(
                    email="admin@unjobshub.com",
                    username="admin",
                    full_name="Admin User",
                    hashed_password=get_password_hash("admin123"),
                    is_admin=True,
                    is_active=True
                )
                session.add(admin_user)
                print("✅ Created admin user (admin@unjobshub.com / admin123)")
            else:
                print("ℹ️  Admin user already exists")

            # Create test regular user
            result = await session.execute(
                select(User).where(User.email == "user@example.com")
            )
            test_user = result.scalar_one_or_none()

            if not test_user:
                test_user = User(
                    email="user@example.com",
                    username="testuser",
                    full_name="Test User",
                    hashed_password=get_password_hash("password123"),
                    is_admin=False,
                    is_active=True
                )
                session.add(test_user)
                print("✅ Created test user (user@example.com / password123)")
            else:
                print("ℹ️  Test user already exists")

            await session.commit()

        await engine.dispose()
        print("\n✅ Test data seeded successfully!")
        print("\n👤 Test Accounts:")
        print("  Admin: admin@unjobshub.com / admin123")
        print("  User:  user@example.com / password123")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        raise


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument(
        "command",
        choices=["check", "create", "tables", "drop", "show", "seed"],
        help="Command to run"
    )

    args = parser.parse_args()

    if args.command == "check":
        asyncio.run(check_database_connection())
    elif args.command == "create":
        asyncio.run(create_database_if_not_exists())
    elif args.command == "tables":
        asyncio.run(create_tables())
    elif args.command == "drop":
        asyncio.run(drop_all_tables())
    elif args.command == "show":
        asyncio.run(show_tables())
    elif args.command == "seed":
        asyncio.run(seed_test_data())


if __name__ == "__main__":
    main()
