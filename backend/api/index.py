"""Vercel serverless function entry point."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import FastAPI app
from main import app

# Vercel expects a handler that can process requests
# For FastAPI, we need to wrap it with Mangum or use the app directly
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    # Fallback: direct app export (may not work perfectly on Vercel)
    handler = app

