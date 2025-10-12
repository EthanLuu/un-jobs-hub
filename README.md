# 🌍 UNJobsHub

> **Your gateway to United Nations careers.** Find, filter, and apply to jobs across the UN system with AI-powered matching.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)

## 📋 Overview

UNJobsHub is a comprehensive job search platform that aggregates positions from across the United Nations system, including UN Secretariat, UNDP, UNICEF, WHO, FAO, UNOPS, and more. The platform features:

- 🔍 **Smart Job Search** - Advanced filtering across 30+ UN organizations
- 🤖 **AI-Powered Matching** - Intelligent resume-to-job matching using OpenAI
- 📄 **Resume Analysis** - Upload and parse PDF/DOCX resumes
- ⭐ **Favorites & Tracking** - Save jobs and track application status
- 🔔 **Job Alerts** - Custom notifications for new matching positions
- 🕷️ **Automated Crawling** - Daily updates from UN career sites

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

4. **Start databases:**
```bash
make db-up
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
│   │   ├── components/      # React components
│   │   │   ├── ui/         # Shadcn/UI components
│   │   │   ├── home/       # Home page components
│   │   │   └── layout/     # Layout components
│   │   └── lib/            # Utilities & API client
│   ├── package.json
│   └── tailwind.config.ts
│
├── backend/                  # FastAPI application
│   ├── main.py              # Application entry point
│   ├── config.py            # Settings & configuration
│   ├── database.py          # Database connection
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
│   │   └── crawl.py
│   ├── services/            # Business logic
│   │   ├── resume_parser.py
│   │   └── matching_service.py
│   ├── crawlers/            # Web scrapers
│   │   ├── base_crawler.py
│   │   ├── un_careers_spider.py
│   │   ├── undp_spider.py
│   │   └── unicef_spider.py
│   ├── utils/               # Helper functions
│   │   └── auth.py
│   ├── celery_app.py        # Celery configuration
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml        # Local development
├── Makefile                  # Development commands
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

## 🤖 AI Features

### Resume Parsing
The system automatically extracts:
- Skills and competencies
- Years of experience
- Education history
- Key achievements

### Job Matching Algorithm
```python
final_score = (keyword_match * 0.7) + (experience_match * 0.3)
```

Factors considered:
- Keyword overlap between resume and job description
- Required vs. actual years of experience
- Education level requirements
- Language proficiency

### OpenAI Integration
When configured, the system uses GPT-4 to provide:
- Personalized application recommendations
- Gap analysis between candidate and requirements
- Career development suggestions

## 🕷️ Web Crawlers

### Supported Organizations
- UN Careers (careers.un.org)
- UNDP (jobs.undp.org)
- UNICEF (unicef.org/careers)
- WHO, FAO, UNOPS (coming soon)

### Crawler Schedule
- **Daily:** 2 AM UTC (GitHub Actions)
- **Manual:** Via admin dashboard
- **Rate Limiting:** Respects robots.txt

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

```bash
# Install all dependencies
make install

# Run development servers
make dev

# Run backend only
make backend

# Run frontend only
make frontend

# Start databases
make db-up

# Stop databases
make db-down

# Run linters
make lint

# Clean temp files
make clean

# Build production images
make build

# Start production stack
make up
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

- JWT-based authentication
- Password hashing with bcrypt
- SQL injection protection via SQLAlchemy
- XSS protection via React
- CORS configuration
- Rate limiting on API endpoints

## 📝 Environment Variables

See `.env.example` for all required variables:

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `REDIS_URL` - Redis connection string

**Optional:**
- `OPENAI_API_KEY` - For AI features
- `SMTP_*` - For email notifications

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



