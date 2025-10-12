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
    engine_kwargs.update({
        "pool_size": 5,  # Minimum number of connections in the pool
        "max_overflow": 10,  # Maximum number of connections beyond pool_size
        "pool_pre_ping": True,  # Verify connections before using them
        "pool_recycle": 3600,  # Recycle connections after 1 hour
    })
    # Add SSL configuration for PostgreSQL (required for Neon and other cloud databases)
    engine_kwargs["connect_args"] = {
        "ssl": "require",  # Required for Neon and most cloud PostgreSQL services
        "server_settings": {
            "application_name": "unjobs_api",
            "jit": "off",  # Disable JIT for better compatibility
        },
    }

engine = create_async_engine(db_url, **engine_kwargs)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,  # Prevent automatic flushes during queries
    autocommit=False,  # Explicit transaction control
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

