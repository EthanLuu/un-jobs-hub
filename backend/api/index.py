"""Vercel serverless function entry point."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import FastAPI app directly
from main import app

# For Vercel, just export the app directly
# Vercel's @vercel/python will handle ASGI
__all__ = ['app']

