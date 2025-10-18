"""Database connection and session management."""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from config import settings

# Create async engine
# Support both PostgreSQL and SQLite
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    # Use psycopg instead of asyncpg for better serverless support
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://")
elif db_url.startswith("postgresql+asyncpg://"):
    # Handle existing asyncpg URLs
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif db_url.startswith("sqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")

# Check if running in serverless environment
is_serverless = os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")

# Configure engine with SSL support for PostgreSQL
engine_kwargs = {
    "echo": settings.debug,
    "future": True,
}

# Add connection pool settings only for PostgreSQL (SQLite doesn't support these)
if "postgresql" in db_url:
    if is_serverless:
        # For serverless environments, use NullPool
        # psycopg handles serverless much better than asyncpg
        engine_kwargs["poolclass"] = NullPool
        engine_kwargs["connect_args"] = {
            "sslmode": "require",
            "connect_timeout": 10,
            # Note: Neon doesn't support jit parameter in pooled connections
        }
    else:
        # For traditional servers, use connection pooling
        engine_kwargs.update({
            "pool_size": 5,
            "max_overflow": 10,
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_timeout": 30,
        })
        engine_kwargs["connect_args"] = {
            "sslmode": "require",
            "connect_timeout": 10,
        }

engine = create_async_engine(db_url, **engine_kwargs)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

