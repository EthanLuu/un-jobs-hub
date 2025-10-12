# 🚀 Quick Start Guide

Get UNJobsHub running locally in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version

# Check Node.js version (need 18+)
node --version

# Check Docker
docker --version
docker-compose --version
```

## Step-by-Step Setup

### 1. Clone & Setup Environment

```bash
# Clone repository
git clone https://github.com/yourusername/un-jobs-hub.git
cd un-jobs-hub

# Copy environment file
cp .env.example .env

# Edit .env with your settings
# At minimum, set:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - DATABASE_URL (use docker-compose defaults or your own)
```

### 2. Start Database Services

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Wait a few seconds for services to be ready
sleep 5

# Verify they're running
docker-compose ps
```

### 3. Setup Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Initialize database
python -c "from database import engine, Base; from models import *; import asyncio; asyncio.run(engine.begin()).__enter__().run_sync(Base.metadata.create_all)"

# Start backend server
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000

### 4. Setup Frontend (New Terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

### 5. Verify Installation

Open your browser:
- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Backend Health:** http://localhost:8000/health

## Optional: Start Celery Workers

For background jobs (crawling, email notifications):

```bash
# Terminal 3: Celery Worker
cd backend
celery -A celery_app worker --loglevel=info

# Terminal 4: Celery Beat (scheduler)
cd backend
celery -A celery_app beat --loglevel=info
```

## Using Make Commands

Or use the Makefile for easier management:

```bash
# Install all dependencies
make install

# Start databases
make db-up

# Run both frontend and backend
make dev

# View all available commands
make help
```

## Create Admin User

```bash
# Using Python shell
cd backend
python

>>> from database import SessionLocal
>>> from models.user import User
>>> from utils.auth import get_password_hash
>>> 
>>> db = SessionLocal()
>>> admin = User(
...     email="admin@unjobs.com",
...     username="admin",
...     hashed_password=get_password_hash("admin123"),
...     full_name="Admin User",
...     is_admin=True
... )
>>> db.add(admin)
>>> db.commit()
>>> exit()
```

## Test the System

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Browse Jobs

Visit http://localhost:3000/jobs

## Populate Test Data

```bash
cd backend
python

>>> from database import SessionLocal
>>> from models.job import Job
>>> from datetime import date, timedelta
>>> 
>>> db = SessionLocal()
>>> 
>>> # Add sample jobs
>>> jobs = [
...     Job(
...         title="Programme Specialist",
...         organization="UNDP",
...         job_id="UNDP-2024-001",
...         description="Exciting opportunity in programme management",
...         category="Programme Management",
...         grade="P-3",
...         location="New York, USA",
...         apply_url="https://jobs.undp.org/example",
...         deadline=date.today() + timedelta(days=30),
...         is_active=True
...     ),
...     Job(
...         title="Human Rights Officer",
...         organization="UN",
...         job_id="UN-2024-001",
...         description="Work on human rights initiatives",
...         category="Human Rights",
...         grade="P-4",
...         location="Geneva, Switzerland",
...         apply_url="https://careers.un.org/example",
...         deadline=date.today() + timedelta(days=20),
...         is_active=True
...     )
... ]
>>> 
>>> for job in jobs:
...     db.add(job)
>>> 
>>> db.commit()
>>> exit()
```

## Trigger Manual Crawl (Admin)

```bash
# Login as admin first to get token
# Then trigger crawl

curl -X POST http://localhost:8000/api/crawl/trigger \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"organization": "undp"}'
```

## Common Issues

### Port Already in Use

```bash
# Find and kill process using port 3000
lsof -ti:3000 | xargs kill -9

# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Database Connection Error

```bash
# Restart database
docker-compose restart postgres

# Check if it's running
docker-compose logs postgres
```

### Module Not Found Error

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. **Read the full README:** [README.md](README.md)
2. **Check deployment guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
3. **Learn about contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
4. **Explore API docs:** http://localhost:8000/docs
5. **Customize the app:** Start modifying components and routes!

## Development Workflow

```bash
# Daily workflow
1. git pull origin main
2. make db-up
3. make dev
4. Make changes
5. git add .
6. git commit -m "Your message"
7. git push origin your-branch
```

## Getting Help

- 📖 Check documentation in `/docs` folder
- 🐛 Open an issue on GitHub
- 💬 Join our community discussions
- 📧 Email: support@unjobshub.com

## Useful Links

- **API Documentation:** http://localhost:8000/docs
- **API Redoc:** http://localhost:8000/redoc
- **Flower (Celery monitor):** http://localhost:5555 (if running)

Happy coding! 🎉



