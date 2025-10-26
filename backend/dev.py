#!/usr/bin/env python3
"""Development utilities and helper scripts."""
import subprocess
import sys
import os
from pathlib import Path


class DevTools:
    """Development utilities."""

    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.project_root = self.backend_dir.parent

    def run_command(self, cmd: list, cwd=None):
        """Run a shell command."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.backend_dir,
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr}")
            return False

    def setup(self):
        """Setup development environment."""
        print("🔧 Setting up development environment...")

        # Create virtual environment
        print("\n1. Creating virtual environment...")
        self.run_command([sys.executable, "-m", "venv", "venv"])

        # Install dependencies
        print("\n2. Installing dependencies...")
        pip = "./venv/bin/pip" if os.name != "nt" else ".\\venv\\Scripts\\pip"
        self.run_command([pip, "install", "-r", "requirements.txt"])
        self.run_command([pip, "install", "-r", "requirements-crawler.txt"])
        self.run_command([pip, "install", "-r", "requirements-test.txt"])

        print("\n✅ Development environment ready!")
        print("\nNext steps:")
        print("  1. Copy .env.example to .env and configure")
        print("  2. Run 'python dev.py db-init' to setup database")
        print("  3. Run 'python dev.py run' to start server")

    def db_init(self):
        """Initialize database."""
        print("🗄️  Initializing database...")

        # Run migrations
        print("\n1. Running Alembic migrations...")
        self.run_command(["alembic", "upgrade", "head"])

        print("\n✅ Database initialized!")

    def db_migrate(self, message: str = None):
        """Create new database migration."""
        msg = message or input("Migration message: ")
        print(f"📝 Creating migration: {msg}")

        self.run_command([
            "alembic", "revision",
            "--autogenerate",
            "-m", msg
        ])

        print("\n✅ Migration created!")
        print("Review the migration file and run 'python dev.py db-upgrade'")

    def db_upgrade(self):
        """Apply database migrations."""
        print("⬆️  Applying database migrations...")
        self.run_command(["alembic", "upgrade", "head"])
        print("\n✅ Database upgraded!")

    def db_downgrade(self, steps: int = 1):
        """Rollback database migrations."""
        print(f"⬇️  Rolling back {steps} migration(s)...")
        self.run_command(["alembic", "downgrade", f"-{steps}"])
        print("\n✅ Database downgraded!")

    def test(self, path: str = "tests/"):
        """Run tests."""
        print("🧪 Running tests...")
        self.run_command([
            "pytest",
            path,
            "-v",
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term"
        ])

    def lint(self):
        """Run linters."""
        print("🔍 Running linters...")

        print("\n1. Running flake8...")
        self.run_command(["flake8", ".", "--max-line-length=100"])

        print("\n2. Running mypy...")
        self.run_command(["mypy", ".", "--ignore-missing-imports"])

        print("\n✅ Linting complete!")

    def format_code(self):
        """Format code with black."""
        print("🎨 Formatting code with black...")
        self.run_command(["black", ".", "--line-length=100"])
        print("\n✅ Code formatted!")

    def run(self, reload: bool = True):
        """Run development server."""
        print("🚀 Starting development server...")
        cmd = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
        if reload:
            cmd.append("--reload")

        subprocess.run(cmd, cwd=self.backend_dir)

    def run_crawlers(self):
        """Run all crawlers."""
        print("🕷️  Running all crawlers...")
        self.run_command([sys.executable, "run_all_crawlers.py"])

    def shell(self):
        """Open Python shell with app context."""
        print("🐍 Opening Python shell...")
        subprocess.run([sys.executable, "-i", "-c", """
import asyncio
from database import get_async_session
from models import *
from config import settings

print("Available imports:")
print("  - asyncio")
print("  - get_async_session")
print("  - models (User, Job, Resume, etc.)")
print("  - settings")
print("")
print("Example:")
print("  async with get_async_session() as db:")
print("      result = await db.execute(select(Job).limit(5))")
print("      jobs = result.scalars().all()")
        """], cwd=self.backend_dir)

    def clean(self):
        """Clean temporary files."""
        print("🧹 Cleaning temporary files...")

        patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.pyd",
            ".pytest_cache",
            ".coverage",
            "htmlcov",
            "*.egg-info",
        ]

        for pattern in patterns:
            for path in self.backend_dir.rglob(pattern):
                if path.is_dir():
                    print(f"  Removing {path}")
                    import shutil
                    shutil.rmtree(path)
                elif path.is_file():
                    print(f"  Removing {path}")
                    path.unlink()

        print("\n✅ Cleanup complete!")

    def check_config(self):
        """Check configuration."""
        print("⚙️  Checking configuration...")
        self.run_command([sys.executable, "-m", "utils.config_validator"])


def main():
    """Main CLI entry point."""
    dev = DevTools()

    commands = {
        "setup": ("Setup development environment", dev.setup),
        "run": ("Run development server", dev.run),
        "test": ("Run tests", dev.test),
        "lint": ("Run linters", dev.lint),
        "format": ("Format code", dev.format_code),
        "db-init": ("Initialize database", dev.db_init),
        "db-migrate": ("Create database migration", dev.db_migrate),
        "db-upgrade": ("Apply database migrations", dev.db_upgrade),
        "db-downgrade": ("Rollback database migrations", dev.db_downgrade),
        "crawl": ("Run all crawlers", dev.run_crawlers),
        "shell": ("Open Python shell", dev.shell),
        "clean": ("Clean temporary files", dev.clean),
        "check-config": ("Check configuration", dev.check_config),
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print("UN Jobs Hub - Development Tools\n")
        print("Usage: python dev.py <command>\n")
        print("Available commands:")
        for cmd, (desc, _) in commands.items():
            print(f"  {cmd:20} - {desc}")
        sys.exit(1)

    command = sys.argv[1]
    _, func = commands[command]
    func()


if __name__ == "__main__":
    main()
