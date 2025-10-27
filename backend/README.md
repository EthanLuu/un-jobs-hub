# UN Jobs Hub - Backend Documentation

> FastAPI backend with PostgreSQL, Redis, and Celery for the UN Jobs Hub platform

## 📋 Overview

The backend is built with **FastAPI 0.109**, providing a high-performance async API for job aggregation, AI-powered matching, and web crawling across 8 UN organizations. The system features comprehensive monitoring, security measures, and developer tools.

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│          FastAPI Application             │
│   (main.py - Async/Await)               │
└──────────────┬──────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────┐    ┌──────────────┐
│PostgreSQL│    │ Redis Cache  │
│  (Async) │    │ (Rate Limit) │
└──────────┘    └──────────────┘
      │                 │
      │                 ▼
      │         ┌──────────────┐
      │         │Celery+Beat   │
      │         │(Crawlers)    │
      │         └──────────────┘
      │                 │
      └─────────────────┘
```

## 🔧 Tech Stack

- **Framework:** FastAPI 0.109 (Python 3.11+)
- **Database:** PostgreSQL 16 with SQLAlchemy 2.0 (async)
- **Cache:** Redis 7 (optional with graceful fallback)
- **Task Queue:** Celery 5.3 + Beat for scheduling
- **Authentication:** JWT (python-jose + passlib)
- **Validation:** Pydantic 2.0
- **Migrations:** Alembic
- **Web Scraping:** Playwright + BeautifulSoup4
- **AI/ML:** OpenAI API, TF-IDF, Levenshtein distance

## 📁 Project Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── config.py                  # Environment configuration (Pydantic Settings)
├── database.py                # Async database connection and session
├── init_db.py                 # Database initialization CLI (6 commands)
├── migrate_db.py              # Alembic migration helper CLI (6 commands)
├── run_all_crawlers.py        # Run all crawlers script
│
├── models/                    # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py               # User model
│   ├── job.py                # Job model (with GIN indexes)
│   ├── resume.py             # Resume model
│   ├── favorite.py           # User favorites
│   └── subscription.py       # Job alerts
│
├── schemas/                   # Pydantic request/response schemas
│   ├── __init__.py
│   ├── user.py
│   ├── job.py
│   ├── resume.py
│   └── ...
│
├── routers/                   # API endpoint routers
│   ├── __init__.py
│   ├── auth.py               # Authentication (register, login, me)
│   ├── jobs.py               # Job CRUD and search
│   ├── favorites.py          # Favorites management
│   ├── resume.py             # Resume upload and parsing
│   ├── match.py              # AI matching endpoints
│   ├── crawl.py              # Crawler management (admin)
│   └── metrics.py            # Monitoring and metrics
│
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── resume_parser.py      # PDF/DOCX parsing
│   └── matching_service.py   # AI matching algorithm
│
├── crawlers/                  # Web scrapers (8 organizations)
│   ├── __init__.py
│   ├── base_crawler.py       # Enhanced base with retry and monitoring
│   ├── un_careers_spider.py  # careers.un.org
│   ├── uncareer_spider.py    # UNCareer.net
│   ├── who_spider.py         # WHO
│   ├── fao_spider.py         # FAO
│   ├── unops_spider.py       # UNOPS
│   ├── ilo_spider.py         # ILO
│   ├── undp_spider.py        # UNDP
│   └── unicef_spider.py      # UNICEF
│
├── utils/                     # Helper utilities
│   ├── __init__.py
│   ├── auth.py               # Password hashing, token generation
│   ├── logger.py             # Structured logging (JSON in prod)
│   ├── monitoring.py         # Performance monitoring middleware
│   ├── crawler_monitoring.py # Crawler health checks
│   ├── keyword_extraction.py # TF-IDF keyword extraction
│   ├── cache.py              # Redis cache manager
│   ├── rate_limit.py         # API rate limiting
│   ├── security.py           # Security headers and validation
│   ├── exceptions.py         # Custom exception classes
│   ├── config_validator.py   # Startup configuration validation
│   └── optimize_db.py        # Database optimization tool
│
├── alembic/                   # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── celery_app.py             # Celery configuration and tasks
├── requirements.txt          # Python dependencies
├── Dockerfile                # Multi-stage production build
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16
- Redis 7 (optional but recommended)

### Installation

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret (use strong random string in production)
- `REDIS_URL` - Redis connection string (optional)

3. **Initialize database:**
```bash
# Check connection
python init_db.py check

# Create tables
python init_db.py tables

# Seed test data (development)
python init_db.py seed
```

4. **Run development server:**
```bash
# With auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

### Authentication
```
POST   /api/auth/register      # Register new user
POST   /api/auth/login         # Login (returns JWT)
GET    /api/auth/me            # Get current user
PUT    /api/auth/me            # Update profile
```

### Jobs
```
GET    /api/jobs               # List jobs (filters, pagination, search)
GET    /api/jobs/{id}          # Get job details
GET    /api/jobs/filters/options  # Get filter options
```

**Query Parameters for GET /api/jobs:**
- `search` - Full-text search
- `organization` - Filter by UN organization
- `location` - Filter by location
- `grade_level` - Filter by grade level
- `contract_type` - Filter by contract type
- `skip`, `limit` - Pagination

### Favorites
```
GET    /api/favorites          # List user's favorites
POST   /api/favorites          # Add to favorites
PUT    /api/favorites/{id}     # Update favorite
DELETE /api/favorites/{id}     # Remove favorite
```

### Resume
```
POST   /api/resume/upload      # Upload PDF/DOCX resume
GET    /api/resume             # List user's resumes
GET    /api/resume/{id}        # Get resume details
DELETE /api/resume/{id}        # Delete resume
```

### Matching
```
POST   /api/match              # Match resume to jobs
GET    /api/match/job/{id}     # Match to specific job
```

### Crawlers (Admin Only)
```
POST   /api/crawl/trigger      # Trigger specific crawler
POST   /api/crawl/trigger-all  # Trigger all crawlers
GET    /api/crawl/status/{id}  # Get crawler task status
GET    /api/crawl/health       # Overall crawler health
GET    /api/crawl/health/{org} # Specific crawler health
GET    /api/crawl/stats        # Aggregated statistics
```

### Monitoring
```
GET    /api/health             # Health check (database status)
GET    /api/metrics            # System metrics (cached 5 min)
```

## 🗄️ Database Schema

### Core Models

**User**
- `id` (UUID, primary key)
- `email` (unique, indexed)
- `username` (unique, indexed)
- `hashed_password`
- `full_name`
- `is_active`, `is_admin`
- `created_at`, `updated_at`

**Job**
- `id` (UUID, primary key)
- `title` (text, indexed)
- `organization` (varchar, indexed)
- `location` (varchar, indexed)
- `grade_level` (varchar, indexed)
- `contract_type` (varchar, indexed)
- `description` (text, GIN indexed for full-text search)
- `responsibilities`, `requirements`, `skills`, `education`, `experience`
- `languages` (JSON array)
- `deadline` (date, indexed)
- `posted_date` (date, indexed)
- `url` (unique)
- `created_at`, `updated_at`

**Resume**
- `id` (UUID, primary key)
- `user_id` (foreign key to User)
- `filename`, `file_path`
- `parsed_skills`, `parsed_experience`, `parsed_education`
- `years_of_experience` (integer)
- `created_at`, `updated_at`

**Favorite**
- `id` (UUID, primary key)
- `user_id` (foreign key to User)
- `job_id` (foreign key to Job)
- `status` (applied, saved, rejected)
- `notes` (text)
- `created_at`, `updated_at`

### Indexes

Performance-critical indexes (created automatically):
- `job.title` - B-tree index
- `job.organization` - B-tree index
- `job.location` - B-tree index
- `job.description` - GIN index for full-text search
- `job.posted_date` - B-tree index (descending)
- Composite indexes for common filter combinations

## 🤖 AI Matching Algorithm

### Multi-Dimensional Scoring

```python
final_score = (
    keyword_match * 0.40 +      # TF-IDF + fuzzy + importance
    experience_match * 0.25 +    # Graduated scoring
    education_match * 0.15 +     # Level comparison
    language_match * 0.12 +      # Fuzzy matching
    location_match * 0.08        # Geographic preference
)
```

### Features (v1.7.0)

**Keyword Extraction (keyword_extraction.py):**
- TF-IDF based extraction with N-grams (bigrams, trigrams)
- Skill importance weighting (1.0-1.5x multipliers)
- Technical skills: 1.4-1.5x (Python, Java, data analysis)
- UN-specific: 1.2-1.3x (humanitarian, peacekeeping)
- Soft skills: 1.0-1.2x (communication, teamwork)

**Fuzzy Matching:**
- Levenshtein distance algorithm
- 0.8 similarity threshold
- Handles typos and variations

**Graduated Scoring:**
- Progressive penalties instead of hard cutoffs
- Experience: 100%+ = 1.0, 75-100% = 0.85, 50-75% = 0.70
- Education: bonus for higher degrees

**Caching:**
- Redis cache with 1-hour TTL
- Key format: `match:{resume_id}:{job_id}`
- Significantly reduces computation for repeated queries

### Implementation

```python
from services.matching_service import calculate_match_score

score_data = await calculate_match_score(resume, job)
# Returns:
# {
#   "score": 0.75,
#   "breakdown": {
#     "keywords": {"score": 0.8, "matching": [...], "missing": [...]},
#     "experience": {"score": 0.7, "years_required": 5, "years_actual": 4},
#     "education": {"score": 1.0, "required": "Bachelor", "actual": "Master"},
#     "languages": {"score": 0.6, "matching": ["English"], "missing": ["French"]},
#     "location": {"score": 0.5}
#   },
#   "recommendations": "Improve French proficiency..."
# }
```

## 🕷️ Web Crawlers

### Supported Organizations (8 Total)

1. **UN Careers** (`un_careers_spider.py`) - careers.un.org
2. **UNCareer.net** (`uncareer_spider.py`) - UNCareer.net
3. **WHO** (`who_spider.py`) - World Health Organization
4. **FAO** (`fao_spider.py`) - Food and Agriculture Org
5. **UNOPS** (`unops_spider.py`) - Project Services
6. **ILO** (`ilo_spider.py`) - International Labour Org
7. **UNDP** (`undp_spider.py`) - Development Programme
8. **UNICEF** (`unicef_spider.py`) - Children's Fund

### Base Crawler Features (v1.6.0)

**Enhanced BaseCrawler** (`base_crawler.py`):
- Exponential backoff retry (3 attempts max)
- Batch database commits (every 10 records)
- Comprehensive metrics collection
- Field validation
- Automatic error recovery
- Health monitoring integration

**Metrics Tracked:**
- Start/end time, duration
- Jobs found/saved/updated/failed
- Success rate (%)
- Retry count
- Error history

**Example Usage:**
```python
from crawlers.un_careers_spider import UNCareersSpider

crawler = UNCareersSpider()
await crawler.crawl()  # Runs with automatic retry and monitoring
```

### Crawler Monitoring (v1.6.0)

**Health Checks** (`utils/crawler_monitoring.py`):
- **HEALTHY**: Last run <24h, success rate >80%
- **WARNING**: Last run <48h, success rate >50%
- **CRITICAL**: Last run >48h or success rate <50%

**API Endpoints:**
```bash
# Get health overview
curl http://localhost:8000/api/crawl/health

# Response:
{
  "overall_health": "WARNING",
  "crawlers": [
    {
      "organization": "UN_CAREERS",
      "health": "HEALTHY",
      "last_run": "2024-01-15T10:30:00Z",
      "success_rate": 95.5,
      "total_runs": 100
    },
    ...
  ]
}
```

### Celery Scheduling

Crawlers run automatically via Celery Beat:

```python
# Staggered schedule (1-8 AM UTC)
"crawl-un-careers": {
    "task": "celery_app.crawl_un_careers_task",
    "schedule": crontab(hour=1, minute=0)
},
"crawl-who": {
    "task": "celery_app.crawl_who_task",
    "schedule": crontab(hour=3, minute=0)
},
...
```

## 🛡️ Security Features

### Authentication (v1.0.0)
- JWT tokens with configurable expiration
- Bcrypt password hashing
- Secure token validation

### Security Headers (v1.4.0)
Automatically added via middleware:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy`
- `Referrer-Policy: strict-origin-when-cross-origin`

### Rate Limiting (v1.3.0)
Sliding window algorithm:
```python
# Default limits (configurable)
RATE_LIMITS = {
    "/api/auth/login": "5 per minute",
    "/api/auth/register": "3 per hour",
    "default": "100 per minute"
}
```

### Input Validation (v1.4.0)
- Query parameter length limits
- Path length validation
- Header size restrictions
- File extension validation
- Input sanitization

## 📊 Monitoring & Logging

### Performance Monitoring (v1.1.0)

**Middleware** (`utils/monitoring.py`):
- Request ID tracking (X-Request-ID header)
- Response time measurement
- Slow request detection (>1 second)
- Automatic logging of errors

**Usage:**
```python
# Automatically applied to all requests
# Check logs for performance data
INFO - Request: GET /api/jobs [200] - 45ms
WARNING - Slow request: GET /api/match [200] - 1523ms
```

### Structured Logging (v1.5.0)

**Features** (`utils/logger.py`):
- Environment-aware format (human-readable in dev, JSON in prod)
- Request context tracking (request_id, method, path, client_host)
- Structured logger with additional fields
- Automatic exception stack traces

**Usage:**
```python
from utils.logger import get_logger, StructuredLogger

logger = get_logger(__name__)
logger.info("Processing job", extra={"job_id": job.id})

# Structured logging
struct_logger = StructuredLogger(__name__)
struct_logger.info_structured(
    "Job processed",
    job_id=job.id,
    duration_ms=123,
    success=True
)
```

### Metrics Endpoint (v1.1.0)

```bash
GET /api/metrics

# Response (cached 5 minutes):
{
  "total_jobs": 1234,
  "total_users": 567,
  "total_favorites": 890,
  "jobs_by_organization": {
    "WHO": 234,
    "UNDP": 345,
    ...
  },
  "jobs_last_7_days": 45,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🛠️ Development Tools

### Database Management (v1.9.0)

**init_db.py** - Database initialization CLI:
```bash
# Check database connection
python init_db.py check

# Create database (if doesn't exist)
python init_db.py create

# Create all tables
python init_db.py tables

# Show all tables
python init_db.py show

# Seed test data (creates admin and test users)
python init_db.py seed
# Admin: admin@unjobshub.com / admin123
# User: user@example.com / password123

# Drop all tables (requires confirmation)
python init_db.py drop
```

**migrate_db.py** - Alembic migration helper:
```bash
# Create new migration
python migrate_db.py create "Add new field"

# Apply migrations
python migrate_db.py upgrade

# Rollback one migration
python migrate_db.py downgrade

# Show current version
python migrate_db.py current

# Show migration history
python migrate_db.py history

# Stamp database with version (without running migration)
python migrate_db.py stamp <revision>
```

### Database Optimization (v1.4.0)

**optimize_db.py** - Performance analysis:
```bash
# Run comprehensive analysis
python utils/optimize_db.py

# Reports:
# - Table sizes
# - Index usage statistics
# - Missing index suggestions
# - Slow queries
# - Table bloat detection
# - Cache hit rates
```

### Configuration Validation (v1.2.0)

Automatic startup validation:
```python
# Runs on application start
- Database connection check
- Required environment variables
- Production-specific checks (SECRET_KEY strength, etc.)
- Configuration summary
```

## 🚀 Deployment

### Environment Configuration

```bash
# Required
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=<strong-random-key>

# Redis (optional but recommended)
REDIS_URL=redis://localhost:6379/0

# OpenAI (for AI matching)
OPENAI_API_KEY=sk-...

# Email (for notifications)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=password

# Celery (defaults to REDIS_URL if not set)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Application
APP_NAME="UNJobsHub API"
DEBUG=false
ENVIRONMENT=production  # development, staging, production
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Production Deployment

**1. Build Docker image:**
```bash
docker build -t unjobshub-backend .
```

**2. Run with Docker Compose:**
```bash
docker-compose up -d
```

**3. Railway deployment:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

**4. Health check:**
```bash
curl https://your-api.railway.app/api/health
```

### Database Migrations in Production

```bash
# Before deploying new version
python migrate_db.py upgrade

# Or in Docker
docker exec -it unjobshub-backend python migrate_db.py upgrade
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_auth.py -v
```

## 📝 Code Standards

### Import Order
```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
from fastapi import FastAPI, Depends
from sqlalchemy import select

# 3. Local
from config import settings
from models.user import User
```

### Async/Await
Always use async for database operations:
```python
# Good
async def get_jobs(db: AsyncSession):
    result = await db.execute(select(Job))
    return result.scalars().all()

# Bad (don't use sync in async context)
def get_jobs(db: Session):
    return db.query(Job).all()
```

### Error Handling
```python
from utils.exceptions import NotFoundException, DatabaseException

# Raise custom exceptions
if not job:
    raise NotFoundException(f"Job {job_id} not found")

# Use try-except for external services
try:
    result = await external_api_call()
except ExternalServiceError as e:
    logger.error("External service failed", exc_info=True)
    raise
```

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write docstrings for public functions
4. Add tests for new features
5. Update this README for significant changes

## 📄 License

MIT License - See [LICENSE](../LICENSE) file

---

**Version:** 1.10.0
**Last Updated:** 2024-12-19
**Maintainer:** UN Jobs Hub Team
