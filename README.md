# 🌍 UNJobsHub

> **Your gateway to United Nations careers.** Find, filter, and apply to jobs across the UN system with AI-powered matching.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.10.0-blue.svg)](https://github.com/yourusername/un-jobs-hub/releases)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)

## 📋 Overview

UNJobsHub is a comprehensive job search platform that aggregates positions from across the United Nations system, including UN Secretariat, UNDP, UNICEF, WHO, FAO, UNOPS, and more. The platform features:

- 🔍 **Smart Job Search** - Advanced filtering across 8 UN organizations with full-text search
- 🤖 **AI-Powered Matching** - Multi-dimensional matching (TF-IDF, fuzzy matching, skill weighting)
- 📄 **Resume Analysis** - Upload and parse PDF/DOCX resumes with intelligent field extraction
- ⭐ **Favorites & Tracking** - Save jobs and track application status
- 🔔 **Job Alerts** - Custom notifications for new matching positions
- 🕷️ **Automated Crawling** - Daily updates from 8 UN organizations with health monitoring
- 📊 **Performance Monitoring** - Real-time API metrics and slow request detection
- 🔐 **Enterprise Security** - Rate limiting, input validation, security headers
- 🛠️ **Developer Tools** - Database migration tools, CLI utilities, structured logging

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   Frontend (Next.js 15 + Tailwind 4)   │
│  Vercel Deployment │ App Router + SWR  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Backend API (FastAPI + PostgreSQL)     │
│  Railway Deployment │ JWT Auth │ Celery │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Crawlers (Playwright + Scrapy)         │
│  GitHub Actions / Railway Cron          │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 16
- Redis 7

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/un-jobs-hub.git
cd un-jobs-hub
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Install dependencies:**
```bash
make install
```

4. **Initialize database:**
```bash
# Check database connection
python backend/init_db.py check

# Create tables
python backend/init_db.py tables

# Seed test data (development only)
python backend/init_db.py seed
```

5. **Run development servers:**
```bash
# Terminal 1: Backend
make backend

# Terminal 2: Frontend
make frontend
```

Or run both simultaneously:
```bash
make dev
```

Visit:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📦 Project Structure

```
un-jobs-hub/
├── frontend/                 # Next.js 15 application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   │   ├── [locale]/   # Internationalized routes
│   │   │   ├── auth/       # Authentication pages
│   │   │   └── api/        # API routes
│   │   ├── components/      # React components
│   │   │   ├── ui/         # Shadcn/UI components
│   │   │   ├── home/       # Home page components
│   │   │   ├── jobs/       # Job listing components
│   │   │   └── layout/     # Layout components
│   │   └── lib/            # Utilities & API client
│   │       ├── api.ts      # Enhanced API client with retry
│   │       ├── api-errors.ts # Typed error handling
│   │       └── lazy-load.tsx # Lazy loading utilities
│   ├── package.json
│   └── tailwind.config.ts
│
├── backend/                  # FastAPI application
│   ├── main.py              # Application entry point
│   ├── config.py            # Settings & configuration
│   ├── database.py          # Database connection
│   ├── init_db.py           # Database initialization CLI
│   ├── migrate_db.py        # Migration helper CLI
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── job.py
│   │   ├── favorite.py
│   │   ├── resume.py
│   │   └── subscription.py
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API endpoints
│   │   ├── auth.py
│   │   ├── jobs.py
│   │   ├── favorites.py
│   │   ├── resume.py
│   │   ├── match.py
│   │   ├── crawl.py
│   │   └── metrics.py       # Monitoring endpoints
│   ├── services/            # Business logic
│   │   ├── resume_parser.py
│   │   └── matching_service.py  # Enhanced AI matching
│   ├── crawlers/            # Web scrapers (8 organizations)
│   │   ├── base_crawler.py   # Enhanced base with monitoring
│   │   ├── un_careers_spider.py
│   │   ├── uncareer_spider.py
│   │   ├── who_spider.py
│   │   ├── fao_spider.py
│   │   ├── unops_spider.py
│   │   ├── ilo_spider.py
│   │   ├── undp_spider.py
│   │   └── unicef_spider.py
│   ├── utils/               # Helper functions
│   │   ├── auth.py
│   │   ├── logger.py         # Structured logging
│   │   ├── monitoring.py     # Performance monitoring
│   │   ├── crawler_monitoring.py  # Crawler health checks
│   │   ├── keyword_extraction.py  # TF-IDF extraction
│   │   ├── cache.py          # Redis cache manager
│   │   ├── rate_limit.py     # API rate limiting
│   │   └── security.py       # Security utilities
│   ├── alembic/             # Database migrations
│   ├── celery_app.py        # Celery configuration
│   ├── requirements.txt
│   └── Dockerfile
│
├── .github/
│   └── workflows/           # CI/CD pipelines
│       └── ci-cd.yml        # Automated testing & deployment
├── docker-compose.yml        # Local development
├── Makefile                  # Development commands
├── PROJECT_STATUS.md         # Project status report
├── CHANGELOG.md              # Detailed version history
└── README.md
```

## 🔧 Technology Stack

### Frontend
- **Framework:** Next.js 15 (App Router, React 19)
- **Styling:** Tailwind CSS 4.0
- **UI Components:** Shadcn/UI + Radix UI
- **State Management:** SWR for data fetching
- **Animations:** Framer Motion
- **Type Safety:** TypeScript 5

### Backend
- **Framework:** FastAPI 0.109
- **Database:** PostgreSQL 16 (via SQLAlchemy 2.0)
- **Cache/Queue:** Redis 7
- **Task Queue:** Celery 5.3
- **Authentication:** JWT (python-jose)
- **Web Scraping:** Playwright + Scrapy
- **AI/ML:** OpenAI API, Sentence Transformers

### DevOps & Deployment
- **Frontend Hosting:** Vercel
- **Backend Hosting:** Railway
- **Database:** Supabase / Railway PostgreSQL
- **Cache:** Upstash Redis
- **CI/CD:** GitHub Actions
- **Containerization:** Docker & Docker Compose

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Jobs
- `GET /api/jobs` - List jobs (with filters & pagination)
- `GET /api/jobs/{id}` - Get job details
- `GET /api/jobs/filters/options` - Get filter options

### Favorites
- `GET /api/favorites` - List user's favorites
- `POST /api/favorites` - Add job to favorites
- `PUT /api/favorites/{id}` - Update favorite
- `DELETE /api/favorites/{id}` - Remove favorite

### Resume
- `POST /api/resume/upload` - Upload resume
- `GET /api/resume` - List user's resumes
- `GET /api/resume/{id}` - Get resume details
- `DELETE /api/resume/{id}` - Delete resume

### Matching
- `POST /api/match` - Match resume to jobs
- `GET /api/match/job/{job_id}` - Match to specific job

### Crawler (Admin Only)
- `POST /api/crawl/trigger` - Trigger crawler
- `GET /api/crawl/status/{task_id}` - Get crawler status
- `POST /api/crawl/trigger-all` - Trigger all crawlers
- `GET /api/crawl/health` - Get overall crawler health
- `GET /api/crawl/health/{organization}` - Get specific crawler health
- `GET /api/crawl/stats` - Get aggregated crawler statistics

### Monitoring & Metrics
- `GET /api/health` - Health check endpoint (database connection status)
- `GET /api/metrics` - System metrics (job counts, user stats, org distribution)

## 🤖 AI Features

### Resume Parsing
The system automatically extracts:
- Skills and competencies
- Years of experience
- Education history
- Key achievements

### Job Matching Algorithm

**Multi-dimensional scoring system:**
```python
final_score = (
    keyword_match * 0.40 +      # TF-IDF + fuzzy matching + importance weighting
    experience_match * 0.25 +    # Graduated scoring with years of experience
    education_match * 0.15 +     # Education level comparison
    language_match * 0.12 +      # Language proficiency (fuzzy matching)
    location_match * 0.08        # Geographic preferences
)
```

**Advanced Features:**
- **TF-IDF Keyword Extraction** - Intelligent phrase detection with N-grams
- **Fuzzy Matching** - Levenshtein distance algorithm (0.8 threshold)
- **Skill Importance Weighting** - Technical skills weighted 1.4-1.5x
- **Graduated Scoring** - Progressive penalties instead of hard cutoffs
- **Redis Caching** - 1-hour cache for match results

Factors considered:
- Keyword overlap with importance weighting (40%)
- Required vs. actual years of experience (25%)
- Education level requirements (15%)
- Language proficiency with fuzzy matching (12%)
- Geographic location preferences (8%)

### OpenAI Integration
When configured, the system uses GPT-4 to provide:
- Personalized application recommendations
- Gap analysis between candidate and requirements
- Career development suggestions

## 🕷️ Web Crawlers

### Supported Organizations (8 Total)
1. **UN Careers** - careers.un.org (Official UN Secretariat)
2. **UNCareer.net** - UNCareer.net (Internships, formal, vacant positions)
3. **WHO** - World Health Organization
4. **FAO** - Food and Agriculture Organization
5. **UNOPS** - United Nations Office for Project Services
6. **ILO** - International Labour Organization
7. **UNDP** - United Nations Development Programme
8. **UNICEF** - United Nations Children's Fund

### Crawler Features
- **Intelligent Field Extraction** - Responsibilities, requirements, education, experience
- **Multi-language Support** - Automatic language detection
- **Anti-bot Countermeasures** - User agents, delays, retry mechanisms
- **Error Handling** - Exponential backoff retry with detailed logging
- **Batch Processing** - Efficient database commits (every 10 records)
- **Health Monitoring** - Real-time health checks and metrics collection

### Crawler Schedule
- **Daily:** Staggered schedule (1-8 AM UTC) via Celery Beat
- **Manual:** Via admin dashboard or CLI
- **Rate Limiting:** Respects robots.txt and includes delays
- **Health Checks:** Three-level system (HEALTHY/WARNING/CRITICAL)

### Monitoring API
```bash
# Get overall crawler health
GET /api/crawl/health

# Get specific crawler details
GET /api/crawl/health/{organization}

# Get aggregated statistics
GET /api/crawl/stats
```

## 🚀 Deployment

### Frontend (Vercel)

1. Connect GitHub repository to Vercel
2. Set environment variables:
   - `NEXT_PUBLIC_API_URL`
3. Deploy automatically on push to `main`

```bash
# Or deploy manually
cd frontend
vercel --prod
```

### Backend (Railway)

1. Create new Railway project
2. Connect GitHub repository
3. Set environment variables (see `.env.example`)
4. Deploy:

```bash
railway up
```

### Database Setup

**Option 1: Supabase**
```bash
# Install Supabase CLI
npm install -g supabase

# Initialize
supabase init
supabase db push
```

**Option 2: Railway PostgreSQL**
- Add PostgreSQL plugin in Railway dashboard
- Copy DATABASE_URL to environment variables

## 📊 Development Commands

### Quick Start
```bash
# Install all dependencies
make install

# Run development servers
make dev

# Run backend only
make backend

# Run frontend only
make frontend
```

### Database Management
```bash
# Start databases (PostgreSQL + Redis)
make db-up

# Stop databases
make db-down

# Check database connection
python backend/init_db.py check

# Create all tables
python backend/init_db.py tables

# Seed test data (creates admin and test users)
python backend/init_db.py seed

# Show all tables
python backend/init_db.py show

# Drop all tables (requires confirmation)
python backend/init_db.py drop
```

### Database Migrations (Alembic)
```bash
# Create a new migration
python backend/migrate_db.py create "Add new field"

# Apply migrations
python backend/migrate_db.py upgrade

# Rollback migration
python backend/migrate_db.py downgrade

# Show current version
python backend/migrate_db.py current

# Show migration history
python backend/migrate_db.py history

# Stamp database version
python backend/migrate_db.py stamp <revision>
```

### Code Quality
```bash
# Run linters
make lint

# Format code
make format

# Type checking
make typecheck
```

### Build & Deploy
```bash
# Build production images
make build

# Start production stack
make up

# Stop production stack
make down

# Clean temp files
make clean
```

### Crawler Management
```bash
# Run all crawlers
python backend/run_all_crawlers.py

# Run specific crawler
python backend/crawlers/un_careers_spider.py

# Check crawler health
curl http://localhost:8000/api/crawl/health
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test

# E2E tests
npm run test:e2e
```

## 🔐 Security

### Authentication & Authorization
- **JWT-based authentication** with secure token generation
- **Password hashing** with bcrypt (strong hashing algorithm)
- **Role-based access control** (admin and user roles)

### Data Protection
- **SQL injection protection** via SQLAlchemy ORM
- **XSS protection** via React and Content Security Policy
- **Input validation** with length and format checks
- **File upload validation** with type and size restrictions

### Security Headers (v1.4.0)
- **X-Frame-Options** - Prevents clickjacking attacks
- **X-Content-Type-Options** - Prevents MIME sniffing
- **X-XSS-Protection** - Browser XSS protection
- **Strict-Transport-Security** - HSTS enforcement
- **Content-Security-Policy** - CSP protection
- **Referrer-Policy** - Referrer information control
- **Permissions-Policy** - Feature permissions

### API Security
- **Rate limiting** - Sliding window algorithm (v1.3.0)
  - Configurable limits per endpoint
  - IP and user-based throttling
  - Automatic 429 responses
- **CORS configuration** - Controlled cross-origin requests
- **Input sanitization** - Automatic input cleaning
- **Request timeouts** - 30-second default timeout (v1.8.0)

### Monitoring & Logging
- **Request ID tracking** - Distributed tracing support (v1.1.0)
- **Structured logging** - JSON format in production (v1.5.0)
- **Performance monitoring** - Slow request detection (v1.1.0)
- **Error tracking** - Comprehensive exception handling (v1.2.0)

## 📝 Environment Variables

See `.env.example` for all required variables:

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `REDIS_URL` - Redis connection string

**Optional:**
- `OPENAI_API_KEY` - For AI features
- `SMTP_*` - For email notifications

## 📚 Documentation

Comprehensive documentation is available in the following files:

- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Complete project status, features, and roadmap
- **[CHANGELOG.md](CHANGELOG.md)** - Detailed version history from v1.0.0 to v1.10.0
- **[Backend README](backend/README.md)** - Backend architecture and API documentation
- **[Frontend README](frontend/README.md)** - Frontend architecture and component guide
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions

### Version History Highlights

- **v1.10.0** - Comprehensive documentation (README, Backend, Frontend, Deployment guides)
- **v1.9.0** - Database migration and initialization tools
- **v1.8.0** - Frontend error handling with retry and toast notifications
- **v1.7.0** - Enhanced AI matching with TF-IDF and fuzzy matching
- **v1.6.0** - Crawler monitoring and health checks
- **v1.5.0** - Structured logging with JSON formatting
- **v1.4.0** - Security enhancements and database optimization
- **v1.3.0** - API rate limiting and Redis caching
- **v1.2.0** - Error handling and logging system
- **v1.1.0** - Performance monitoring and ILO crawler

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- UN system organizations for providing public job data
- Shadcn for the beautiful UI components
- FastAPI and Next.js communities

## 📧 Contact

For questions or support, please open an issue or contact [your-email@example.com](mailto:your-email@example.com).

---

**Built with ❤️ for the UN community**



