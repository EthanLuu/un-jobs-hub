"""Vercel serverless function entry point."""
import sys
import os
from pathlib import Path

# Add parent directory to path
backend_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, backend_dir)

# Set working directory for imports
os.chdir(backend_dir)

# Import and export FastAPI app
# Vercel expects a variable named 'app' that is an ASGI application
from main import app

