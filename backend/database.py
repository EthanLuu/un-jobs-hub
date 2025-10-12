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
        "pool_size": 2,  # Smaller pool for serverless environments
        "max_overflow": 5,  # Reduced overflow
        "pool_pre_ping": True,  # Verify connections before using them
        "pool_recycle": 300,  # Recycle connections after 5 minutes (better for serverless)
        "pool_timeout": 30,  # Wait 30 seconds for a connection
    })
    # Add SSL configuration for PostgreSQL (required for Neon and other cloud databases)
    engine_kwargs["connect_args"] = {
        "ssl": "require",  # Required for Neon and most cloud PostgreSQL services
        "server_settings": {
            "application_name": "unjobs_api",
            "jit": "off",  # Disable JIT for better compatibility
        },
        "timeout": 10,  # Connection timeout
        "command_timeout": 10,  # Command timeout
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

