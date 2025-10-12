# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Always respond in Chinese.

## Project Overview

UNJobsHub is a full-stack job search platform that aggregates United Nations positions across 30+ organizations. It features AI-powered resume-to-job matching using OpenAI, automated web crawling with Playwright, and a modern Next.js 15 frontend with FastAPI backend.

## Development Commands

### Quick Start
```bash
# Install all dependencies (backend + frontend)
make install

# Start databases (PostgreSQL + Redis)
make db-up

# Run both frontend and backend
make dev
```

### Individual Services
```bash
# Backend only (FastAPI on port 8000)
make backend

# Frontend only (Next.js on port 3000)
make frontend

# Stop databases
make db-down
```

### Backend-Specific Commands
```bash
cd backend

# Start API server
uvicorn main:app --reload

# Run Celery worker (for crawling tasks)
celery -A celery_app worker --loglevel=info

# Run Celery Beat (scheduled tasks)
celery -A celery_app beat --loglevel=info

# Initialize database tables
python -c "from database import engine, Base; from models import *; import asyncio; asyncio.run(engine.begin()).__enter__().run_sync(Base.metadata.create_all)"

# Install Playwright browsers (required for crawlers)
playwright install chromium
```

### Frontend-Specific Commands
```bash
cd frontend

# Development server
npm run dev

# Production build
npm run build

# Type checking
npm run type-check

# Lint
npm run lint
```

### Testing
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm run test
```

### Docker
```bash
# Build production images
make build

# Start all services (including workers)
make up

# View logs
make logs

# Stop all services
make down
```

## Architecture

### Backend Structure (FastAPI)

**Core Files:**
- `main.py` - FastAPI app entry point with CORS, lifespan management, and router registration
- `config.py` - Pydantic settings loaded from `.env` (database, Redis, JWT, OpenAI)
- `database.py` - SQLAlchemy async engine setup with PostgreSQL/SQLite support
- `celery_app.py` - Celery configuration with scheduled crawler tasks (2-4 AM UTC)

**Key Modules:**
- `models/` - SQLAlchemy ORM models (User, Job, Favorite, Resume, Subscription)
- `schemas/` - Pydantic request/response schemas for API validation
- `routers/` - API endpoints organized by resource (auth, jobs, favorites, resume, match, crawl)
- `services/` - Business logic:
  - `matching_service.py` - Resume-to-job matching algorithm (70% keyword match + 30% experience)
  - `resume_parser.py` - PDF/DOCX parsing and skill extraction
- `crawlers/` - Web scrapers for UN organizations (Playwright-based)
  - `base_crawler.py` - Shared crawler logic with database save functionality
  - `un_careers_spider.py`, `undp_spider.py`, `unicef_spider.py` - Organization-specific implementations
- `utils/` - Helper functions (JWT auth utilities)

**Database:**
- Uses SQLAlchemy 2.0 with async/await pattern (`AsyncSession`)
- Connection string auto-converts: `postgresql://` → `postgresql+asyncpg://`, `sqlite:///` → `sqlite+aiosqlite:///`
- Tables created automatically via `Base.metadata.create_all` in app lifespan

**Authentication:**
- JWT tokens with configurable expiry (default 30 minutes)
- Password hashing with bcrypt via `passlib`
- Token verification in `utils/auth.py`

### Frontend Structure (Next.js 15)

**App Router Pages:**
- `src/app/page.tsx` - Home page with hero, features, and stats
- `src/app/jobs/` - Job listing and detail pages
- `src/app/profile/` - User profile and saved jobs
- `src/app/recommendations/` - AI-powered job recommendations
- `src/app/layout.tsx` - Root layout with providers

**Components:**
- `src/components/ui/` - Shadcn/UI primitives (Button, Card, Dialog, etc.)
- `src/components/home/` - Home page sections (Hero, FeaturedJobs, Features, Stats)
- `src/components/layout/` - Header and Footer
- `src/components/providers.tsx` - Context providers (auth, theme, etc.)

**Utilities:**
- `src/lib/api.ts` - API client class with methods for all endpoints
  - Uses `NEXT_PUBLIC_API_URL` env var (defaults to `http://localhost:8000`)
  - Handles JWT token storage and authentication headers
- `src/lib/utils.ts` - Helper functions

**Styling:**
- Tailwind CSS 4.0 with custom config
- Shadcn/UI design system
- Framer Motion for animations
- Lucide React for icons

### Data Flow

1. **Job Crawling:** Celery Beat triggers scheduled tasks → Crawlers fetch jobs via Playwright → Save to PostgreSQL via `base_crawler.save_jobs()`
2. **Job Search:** Frontend → `/api/jobs` (with filters) → SQLAlchemy query with pagination → JSON response
3. **Resume Matching:**
   - User uploads PDF/DOCX → `/api/resume/upload` → `resume_parser.py` extracts text/skills
   - Match request → `/api/match` → `matching_service.calculate_match_score()` → Returns score (0-1), matching/missing keywords, AI recommendation
4. **AI Recommendations:** If `OPENAI_API_KEY` set → `get_ai_recommendation()` uses GPT-4 for personalized advice

## Important Patterns

### Async/Await Everywhere
- **Backend:** All route handlers are `async def`, database calls use `await`
- **Database sessions:** Always use `async with AsyncSessionLocal()` or dependency injection via `get_db()`
- **Celery tasks:** Synchronous (use `crawl_*_sync` wrappers that call async functions with `asyncio.run()`)

### Database Session Management
```python
# In routers (dependency injection)
async def endpoint(db: AsyncSession = Depends(get_db)):
    # Session auto-commits on success, rolls back on exception

# In services (manual context manager)
async with AsyncSessionLocal() as session:
    try:
        # ... queries ...
        await session.commit()
    except:
        await session.rollback()
        raise
```

### Celery Synchronous Wrappers
Celery doesn't support async tasks. Crawlers run sync versions:
```python
# In celery_app.py
@celery_app.task
def crawl_un_careers():
    from crawlers.un_careers_spider import crawl_un_careers_sync
    return crawl_un_careers_sync()

# In crawler file
def crawl_un_careers_sync():
    return asyncio.run(crawl_un_careers_async())
```

### API Client Pattern (Frontend)
```typescript
// In components
import { apiClient } from '@/lib/api';

const jobs = await apiClient.getJobs({ organization: 'UNDP', page: 1 });
```

### Environment Variables
- **Backend:** Loaded via `pydantic-settings` from `.env` → `config.py` → `settings` singleton
- **Frontend:** Next.js env vars prefixed with `NEXT_PUBLIC_` for client-side access

## Common Development Tasks

### Adding a New API Endpoint

1. **Define Pydantic schema** in `backend/schemas/`:
```python
from pydantic import BaseModel

class MyRequestSchema(BaseModel):
    field: str

class MyResponseSchema(BaseModel):
    result: str
```

2. **Create route** in `backend/routers/`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

router = APIRouter()

@router.post("/my-endpoint", response_model=MyResponseSchema)
async def my_endpoint(
    request: MyRequestSchema,
    db: AsyncSession = Depends(get_db)
):
    # Logic here
    return {"result": "success"}
```

3. **Register router** in `backend/main.py`:
```python
from routers import my_router
app.include_router(my_router.router, prefix="/api/my", tags=["My Feature"])
```

4. **Add frontend method** in `frontend/src/lib/api.ts`:
```typescript
async myEndpoint(field: string) {
  return this.request('/api/my/my-endpoint', {
    method: 'POST',
    body: JSON.stringify({ field }),
  });
}
```

### Adding a New Database Model

1. **Create model** in `backend/models/`:
```python
from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class MyModel(Base):
    __tablename__ = "my_table"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **Import in `models/__init__.py`**:
```python
from .my_model import MyModel
```

3. **Tables auto-create** on app startup via `Base.metadata.create_all` in `main.py`

For migrations (production), use Alembic:
```bash
cd backend
alembic revision --autogenerate -m "Add my_table"
alembic upgrade head
```

### Adding a New Crawler

1. **Create spider** in `backend/crawlers/`:
```python
from crawlers.base_crawler import BaseCrawler
from playwright.async_api import async_playwright

class MyOrgSpider(BaseCrawler):
    def __init__(self):
        super().__init__(organization="MyOrg")

    async def crawl(self):
        jobs_data = []
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto("https://example.org/jobs")

            # Extract jobs...
            jobs_data.append({
                "job_id": "MYORG-001",
                "title": "Job Title",
                "organization": "MyOrg",
                "description": "...",
                # ... required fields from Job model
            })

            await browser.close()

        return self.save_jobs(jobs_data)

# Sync wrapper
def crawl_myorg_sync():
    import asyncio
    spider = MyOrgSpider()
    return asyncio.run(spider.crawl())
```

2. **Register Celery task** in `backend/celery_app.py`:
```python
@celery_app.task(name="celery_app.crawl_myorg")
def crawl_myorg():
    from crawlers.myorg_spider import crawl_myorg_sync
    return crawl_myorg_sync()

# Add to beat schedule
celery_app.conf.beat_schedule["crawl-myorg-daily"] = {
    "task": "celery_app.crawl_myorg",
    "schedule": crontab(hour=5, minute=0),
}
```

### Testing API Changes

1. **Start backend:** `make backend`
2. **Open API docs:** http://localhost:8000/docs
3. **Interactive testing:** Swagger UI provides "Try it out" for all endpoints
4. **View schemas:** http://localhost:8000/redoc

## Key Configuration

### Required Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/unjobs
SECRET_KEY=<generate with: openssl rand -hex 32>
REDIS_URL=redis://localhost:6379/0

# Optional
OPENAI_API_KEY=sk-...  # For AI features
SMTP_HOST=smtp.gmail.com  # For email notifications
```

### Frontend Environment
```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Docker Compose Defaults
- PostgreSQL: `unjobs:unjobs123@localhost:5432/unjobs`
- Redis: `localhost:6379/0`

## Deployment Notes

- **Frontend:** Vercel (automatic deployment from GitHub)
- **Backend:** Railway (with Dockerfile)
- **Database:** Supabase or Railway PostgreSQL
- **Crawlers:** GitHub Actions (see `.github/workflows/crawl-jobs.yml`)

The `crawl` router is commented out in `main.py` for quick local start (requires Celery). Uncomment for production with proper Celery setup.

## Tech Stack Versions

- **Backend:** Python 3.11+, FastAPI 0.109, SQLAlchemy 2.0, Celery 5.3, Playwright 1.41
- **Frontend:** Next.js 15, React 18, TypeScript 5, Tailwind CSS 3.4
- **Database:** PostgreSQL 16, Redis 7
- **AI:** OpenAI API (GPT-4), Sentence Transformers

## Troubleshooting

### Port conflicts
```bash
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:8000 | xargs kill -9  # Backend
```

### Database connection errors
```bash
docker-compose restart postgres
docker-compose logs postgres
```

### Missing Playwright browsers
```bash
cd backend && playwright install chromium
```

### Module not found
```bash
cd backend && source venv/bin/activate && pip install -r requirements.txt
```
