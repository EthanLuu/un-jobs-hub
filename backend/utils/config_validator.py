"""Environment configuration validator."""
import os
import sys
from typing import List, Dict, Any, Optional
from pydantic import ValidationError


class ConfigValidator:
    """Validate environment configuration."""

    REQUIRED_VARS = [
        "DATABASE_URL",
    ]

    OPTIONAL_VARS = {
        "REDIS_URL": "redis://localhost:6379/0",
        "SECRET_KEY": "change-me-in-production",
        "CELERY_BROKER_URL": "redis://localhost:6379/0",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/0",
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "INFO",
    }

    PRODUCTION_REQUIRED_VARS = [
        "SECRET_KEY",
        "REDIS_URL",
        "CELERY_BROKER_URL",
    ]

    @classmethod
    def validate(cls, strict: bool = True) -> Dict[str, Any]:
        """
        Validate environment configuration.

        Args:
            strict: If True, exit on missing required variables

        Returns:
            Dictionary of validation results
        """
        missing_vars = []
        warnings = []
        config = {}

        # Check required variables
        for var in cls.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                config[var] = value

        # Check optional variables with defaults
        for var, default in cls.OPTIONAL_VARS.items():
            value = os.getenv(var, default)
            config[var] = value
            if value == default and var != "ENVIRONMENT":
                warnings.append(f"{var} is using default value: {default}")

        # Production-specific checks
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            for var in cls.PRODUCTION_REQUIRED_VARS:
                value = os.getenv(var)
                if not value or value == cls.OPTIONAL_VARS.get(var):
                    missing_vars.append(f"{var} (required in production)")

        # Report results
        result = {
            "valid": len(missing_vars) == 0,
            "missing": missing_vars,
            "warnings": warnings,
            "config": config,
        }

        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            if strict:
                print(f"❌ Configuration Error: {error_msg}", file=sys.stderr)
                print("\nPlease set the following environment variables:", file=sys.stderr)
                for var in missing_vars:
                    print(f"  - {var}", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"⚠️  Warning: {error_msg}", file=sys.stderr)

        if warnings and env == "production":
            print("\n⚠️  Production Warnings:", file=sys.stderr)
            for warning in warnings:
                print(f"  - {warning}", file=sys.stderr)

        return result

    @classmethod
    def print_config_summary(cls):
        """Print a summary of the current configuration."""
        from config import settings

        print("\n" + "=" * 60)
        print("UN Jobs Hub - Configuration Summary")
        print("=" * 60)
        print(f"Environment: {settings.environment}")
        print(f"App Name: {settings.app_name}")
        print(f"Debug Mode: {settings.debug}")
        print(f"Log Level: {settings.log_level}")
        print(f"Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'configured'}")
        print(f"Redis: {'configured' if settings.redis_url else 'not configured'}")
        print(f"Celery: {'configured' if settings.celery_broker_url else 'not configured'}")
        print(f"Secret Key: {'configured' if settings.secret_key and settings.secret_key != 'change-me-in-production' else '⚠️  using default'}")
        print("=" * 60)
        print()

    @classmethod
    def check_database_connection(cls) -> bool:
        """Check if database connection is working."""
        try:
            from database import engine
            from sqlalchemy import text
            import asyncio

            async def test_connection():
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    return True

            return asyncio.run(test_connection())
        except Exception as e:
            print(f"❌ Database connection failed: {e}", file=sys.stderr)
            return False

    @classmethod
    def run_startup_checks(cls, strict: bool = True):
        """Run all startup checks."""
        print("\n🔍 Running startup checks...")

        # Validate environment
        result = cls.validate(strict=strict)

        # Print config summary
        if result["valid"]:
            print("✅ Environment configuration valid")
            cls.print_config_summary()

            # Check database connection
            print("🔍 Checking database connection...")
            if cls.check_database_connection():
                print("✅ Database connection successful\n")
            else:
                if strict:
                    print("❌ Database connection failed", file=sys.stderr)
                    sys.exit(1)
                else:
                    print("⚠️  Database connection failed (continuing anyway)\n")
        else:
            print("❌ Environment configuration invalid\n")
            if strict:
                sys.exit(1)


if __name__ == "__main__":
    ConfigValidator.run_startup_checks(strict=False)
