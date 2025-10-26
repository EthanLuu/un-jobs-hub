"""
Database migration helper script.

Provides utilities for managing Alembic migrations.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from alembic import command
from alembic.config import Config
from database import Base, get_engine
from models import user, job, resume, favorite, subscription  # Import all models
import logging

logger = logging.getLogger(__name__)


def get_alembic_config() -> Config:
    """Get Alembic configuration."""
    # Get the backend directory
    backend_dir = Path(__file__).parent
    alembic_ini_path = backend_dir / "alembic.ini"

    if not alembic_ini_path.exists():
        raise FileNotFoundError(f"alembic.ini not found at {alembic_ini_path}")

    config = Config(str(alembic_ini_path))
    config.set_main_option("script_location", str(backend_dir / "alembic"))

    # Get database URL from settings
    from config import settings
    config.set_main_option("sqlalchemy.url", settings.database_url)

    return config


def create_initial_migration(message: str = "Initial migration"):
    """Create initial migration with all models."""
    print(f"Creating initial migration: {message}")

    try:
        config = get_alembic_config()
        command.revision(config, message=message, autogenerate=True)
        print("✅ Initial migration created successfully!")
        print("📋 Review the migration file in alembic/versions/")
        print("🚀 Run 'python migrate_db.py upgrade' to apply the migration")
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        raise


def upgrade(revision: str = "head"):
    """Upgrade database to a specific revision."""
    print(f"Upgrading database to: {revision}")

    try:
        config = get_alembic_config()
        command.upgrade(config, revision)
        print("✅ Database upgraded successfully!")
    except Exception as e:
        print(f"❌ Error upgrading database: {e}")
        raise


def downgrade(revision: str = "-1"):
    """Downgrade database to a specific revision."""
    print(f"Downgrading database to: {revision}")

    try:
        config = get_alembic_config()
        command.downgrade(config, revision)
        print("✅ Database downgraded successfully!")
    except Exception as e:
        print(f"❌ Error downgrading database: {e}")
        raise


def show_current():
    """Show current revision."""
    print("Current database revision:")

    try:
        config = get_alembic_config()
        command.current(config)
    except Exception as e:
        print(f"❌ Error getting current revision: {e}")
        raise


def show_history():
    """Show migration history."""
    print("Migration history:")

    try:
        config = get_alembic_config()
        command.history(config)
    except Exception as e:
        print(f"❌ Error getting history: {e}")
        raise


def stamp(revision: str):
    """Stamp database with a specific revision without running migrations."""
    print(f"Stamping database with revision: {revision}")

    try:
        config = get_alembic_config()
        command.stamp(config, revision)
        print("✅ Database stamped successfully!")
    except Exception as e:
        print(f"❌ Error stamping database: {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database migration helper")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create migration
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")

    # Upgrade
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument(
        "revision", nargs="?", default="head", help="Revision to upgrade to (default: head)"
    )

    # Downgrade
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument(
        "revision", nargs="?", default="-1", help="Revision to downgrade to (default: -1)"
    )

    # Current
    subparsers.add_parser("current", help="Show current revision")

    # History
    subparsers.add_parser("history", help="Show migration history")

    # Stamp
    stamp_parser = subparsers.add_parser("stamp", help="Stamp database with revision")
    stamp_parser.add_argument("revision", help="Revision to stamp")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "create":
            create_initial_migration(args.message)
        elif args.command == "upgrade":
            upgrade(args.revision)
        elif args.command == "downgrade":
            downgrade(args.revision)
        elif args.command == "current":
            show_current()
        elif args.command == "history":
            show_history()
        elif args.command == "stamp":
            stamp(args.revision)
    except Exception as e:
        print(f"\n❌ Command failed: {e}")
        sys.exit(1)
