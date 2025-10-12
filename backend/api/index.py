"""Vercel serverless function entry point."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import FastAPI app
from main import app
from mangum import Mangum

# Create Mangum handler with explicit configuration
handler = Mangum(app, lifespan="off", api_gateway_base_path="/api")

