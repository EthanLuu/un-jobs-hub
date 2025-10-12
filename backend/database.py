"""Database connection and session management."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings

# Create async engine
# Support both PostgreSQL and SQLite
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
elif db_url.startswith("sqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")

# Configure engine with SSL support for PostgreSQL
engine_kwargs = {
    "echo": settings.debug,
    "future": True,
}

# Add connection pool settings only for PostgreSQL (SQLite doesn't support these)
if "postgresql" in db_url:
    # Import os to check if running in serverless environment
    import os
    is_serverless = os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")

    if is_serverless:
        # For serverless environments, use NullPool to avoid connection conflicts
        from sqlalchemy.pool import NullPool
        engine_kwargs["poolclass"] = NullPool
    else:
        # For traditional servers, use connection pooling
        engine_kwargs.update({
            "pool_size": 5,  # Reasonable pool size
            "max_overflow": 10,  # Allow burst traffic
            "pool_pre_ping": True,  # Verify connections before using them
            "pool_recycle": 300,  # Recycle connections after 5 minutes
            "pool_timeout": 30,  # Wait 30 seconds for a connection
            "pool_use_lifo": True,  # Use LIFO to reduce connection switching
        })

    # Add SSL configuration for PostgreSQL (required for Neon and other cloud databases)
    engine_kwargs["connect_args"] = {
        "ssl": "require",  # Required for Neon and most cloud PostgreSQL services
        "server_settings": {
            "application_name": "unjobs_api",
            "jit": "off",  # Disable JIT for better compatibility
        },
        "timeout": 30,  # Increased connection timeout
        "command_timeout": 60,  # Increased command timeout to 60 seconds
    }

engine = create_async_engine(db_url, **engine_kwargs)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
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

