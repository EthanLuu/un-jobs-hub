# UN Jobs Hub - Deployment Guide

> Complete production deployment guide for frontend and backend

## 📋 Overview

This guide covers deploying the UN Jobs Hub platform to production using:
- **Frontend:** Vercel (recommended) or self-hosted
- **Backend:** Railway (recommended) or Docker
- **Database:** Neon, Supabase, or Railway PostgreSQL
- **Cache:** Upstash Redis or Railway Redis

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   Frontend (Vercel)                     │
│   next-app.vercel.app                   │
└──────────────┬──────────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────────┐
│   Backend (Railway)                     │
│   api.railway.app                       │
└──────────────┬──────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────┐    ┌──────────────┐
│PostgreSQL│    │ Redis Cache  │
│(Neon/RW) │    │(Upstash/RW)  │
└──────────┘    └──────────────┘
```

## 🚀 Quick Deployment

### Prerequisites

- GitHub account
- Vercel account
- Railway account
- Domain name (optional)

### 1. Database Setup (Neon PostgreSQL)

**Why Neon:**
- Free tier with 0.5 GB storage
- Serverless PostgreSQL
- Automatic backups
- Connection pooling

**Steps:**
1. Go to [Neon](https://neon.tech)
2. Create new project
3. Copy connection string (looks like):
   ```
   postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```
4. Save as `DATABASE_URL`

**Alternative: Railway PostgreSQL**
1. In Railway, click "New" → "Database" → "PostgreSQL"
2. Copy `DATABASE_URL` from variables tab

### 2. Redis Setup (Upstash)

**Why Upstash:**
- Free tier with 10,000 requests/day
- Serverless Redis
- Global edge caching

**Steps:**
1. Go to [Upstash](https://upstash.com)
2. Create new database
3. Copy Redis URL:
   ```
   redis://default:xxx@usw1-xxx.upstash.io:6379
   ```
4. Save as `REDIS_URL`

**Alternative: Railway Redis**
1. In Railway, click "New" → "Database" → "Redis"
2. Copy `REDIS_URL` from variables tab

### 3. Backend Deployment (Railway)

1. **Connect Repository:**
   - Go to [Railway](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `un-jobs-hub` repository
   - Select `backend` as root directory

2. **Set Environment Variables:**

Click "Variables" tab and add:

```bash
# Required
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
SECRET_KEY=<generate-strong-random-key-min-32-chars>
REDIS_URL=redis://default:xxx@host:6379

# Application
APP_NAME=UNJobsHub API
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# CORS (add frontend URL)
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://unjobshub.com

# OpenAI (optional)
OPENAI_API_KEY=sk-xxx

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Celery (auto-configured from REDIS_URL if not set)
CELERY_BROKER_URL=$REDIS_URL
CELERY_RESULT_BACKEND=$REDIS_URL
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. **Configure Build Settings:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Deploy:**
   - Railway will auto-deploy on push to `main`
   - Get deployment URL from Railway dashboard
   - Example: `https://un-jobs-hub-production.up.railway.app`

5. **Run Database Migrations:**
   ```bash
   # In Railway dashboard, open terminal
   python init_db.py check
   python init_db.py tables
   ```

### 4. Frontend Deployment (Vercel)

1. **Connect Repository:**
   - Go to [Vercel](https://vercel.com)
   - Click "Add New" → "Project"
   - Import `un-jobs-hub` from GitHub
   - Set root directory to `frontend`

2. **Set Environment Variables:**

Click "Environment Variables" and add:

```bash
# Required
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Optional (for analytics, monitoring)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

3. **Configure Build Settings:**
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

4. **Deploy:**
   - Click "Deploy"
   - Vercel will build and deploy
   - Get deployment URL: `https://un-jobs-hub.vercel.app`

5. **Custom Domain (Optional):**
   - Go to "Settings" → "Domains"
   - Add your domain
   - Update DNS records as instructed

## 🔒 Security Checklist

### Before Going Live

- [ ] Change `SECRET_KEY` to strong random value (min 32 characters)
- [ ] Set `DEBUG=false` in production
- [ ] Set `ENVIRONMENT=production`
- [ ] Use HTTPS for all URLs
- [ ] Enable database SSL (`?sslmode=require` in DATABASE_URL)
- [ ] Set strong database password
- [ ] Configure CORS with specific origins (no wildcards)
- [ ] Enable rate limiting (auto-enabled in v1.3.0+)
- [ ] Set up monitoring and error tracking
- [ ] Review and test all API endpoints
- [ ] Test authentication flow
- [ ] Verify file upload restrictions
- [ ] Check security headers are applied

### Generate Secure SECRET_KEY

```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: OpenSSL
openssl rand -base64 32

# Option 3: pwgen
pwgen -s 64 1
```

## 🛠️ Database Setup

### Option 1: Neon (Recommended)

**Pros:**
- Serverless (pay-as-you-go)
- Automatic backups
- Connection pooling
- Free tier: 0.5 GB storage

**Setup:**
```bash
# 1. Create database at neon.tech
# 2. Get connection string
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# 3. Run migrations
python backend/migrate_db.py upgrade
```

### Option 2: Supabase

**Pros:**
- Full Postgres features
- Built-in auth (if needed)
- Free tier: 500 MB storage

**Setup:**
```bash
# 1. Create project at supabase.com
# 2. Get connection string (use "Connection pooling" URL)
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

# 3. Run migrations
python backend/migrate_db.py upgrade
```

### Option 3: Railway PostgreSQL

**Pros:**
- Integrated with backend
- Easy setup
- $5/month

**Setup:**
```bash
# 1. In Railway project, add PostgreSQL plugin
# 2. Copy DATABASE_URL from variables
# 3. Run migrations in Railway terminal
python migrate_db.py upgrade
```

## 📊 Monitoring Setup

### Health Checks

Backend provides health check endpoint:
```bash
curl https://your-backend.railway.app/api/health

# Response:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Set up monitoring:**
1. Use Railway's built-in metrics
2. Or use external monitoring (UptimeRobot, Better Uptime)
3. Monitor `/api/health` endpoint every 5 minutes

### Error Tracking

**Option 1: Sentry**
```bash
# Install
pip install sentry-sdk[fastapi]

# Configure in main.py
import sentry_sdk
sentry_sdk.init(
    dsn="https://xxx@xxx.ingest.sentry.io/xxx",
    environment=settings.environment,
)
```

**Option 2: Railway Logs**
- View logs in Railway dashboard
- Filter by error level
- Set up log drains to external service

### Performance Monitoring

Built-in monitoring (v1.1.0+):
```bash
# View metrics
curl https://your-backend.railway.app/api/metrics

# Response includes:
# - Total jobs, users, favorites
# - Jobs by organization
# - Recent activity
```

## 🔄 CI/CD Pipeline

### GitHub Actions (Included)

Workflow file: `.github/workflows/ci-cd.yml`

**Triggers:**
- On push to `main` branch
- On pull requests

**Steps:**
1. Install dependencies
2. Run linters and type checks
3. Run tests
4. Build Docker image (backend)
5. Build Next.js (frontend)
6. Run security scan (Trivy)
7. Deploy to Railway (backend)
8. Deploy to Vercel (frontend)
9. Run smoke tests

**Required Secrets:**
Add in GitHub Settings → Secrets:
- `RAILWAY_TOKEN` - Railway API token
- `VERCEL_TOKEN` - Vercel API token
- `VERCEL_ORG_ID` - Vercel organization ID
- `VERCEL_PROJECT_ID` - Vercel project ID

### Manual Deployment

**Backend (Railway):**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

**Frontend (Vercel):**
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod
```

## 🌐 Custom Domain Setup

### Frontend (Vercel)

1. Go to Vercel dashboard → Project → Settings → Domains
2. Add your domain: `unjobshub.com`
3. Add DNS records at your domain registrar:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com

   Type: A
   Name: @
   Value: 76.76.21.21
   ```
4. Wait for DNS propagation (up to 48 hours)
5. Vercel will auto-provision SSL certificate

### Backend (Railway)

1. Go to Railway dashboard → Project → Settings → Domains
2. Add custom domain: `api.unjobshub.com`
3. Add DNS record:
   ```
   Type: CNAME
   Name: api
   Value: <your-project>.railway.app
   ```
4. Railway will auto-provision SSL

### Update CORS Settings

After setting up domains, update backend environment:
```bash
ALLOWED_ORIGINS=https://unjobshub.com,https://www.unjobshub.com
```

And update frontend:
```bash
NEXT_PUBLIC_API_URL=https://api.unjobshub.com
```

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Errors**
```
Error: could not connect to server
```

**Solutions:**
- Verify DATABASE_URL is correct
- Check database is running
- Ensure `?sslmode=require` is in connection string
- Verify IP allowlist (if using Supabase)

**2. CORS Errors**
```
Access to fetch at 'api.railway.app' from origin 'vercel.app' has been blocked by CORS
```

**Solutions:**
- Add frontend URL to `ALLOWED_ORIGINS`
- Restart backend after changing environment variables
- Check that URLs don't have trailing slashes

**3. Build Errors (Frontend)**
```
Error: Environment variable NEXT_PUBLIC_API_URL is not defined
```

**Solutions:**
- Add `NEXT_PUBLIC_API_URL` in Vercel environment variables
- Redeploy after adding variables

**4. 500 Errors**
```
Internal Server Error
```

**Solutions:**
- Check Railway logs for stack trace
- Verify all required environment variables are set
- Check database migrations are up to date
- Verify SECRET_KEY is set

**5. Slow Response Times**

**Solutions:**
- Enable Redis caching
- Check database indexes (run `python utils/optimize_db.py`)
- Monitor slow requests in logs
- Consider upgrading Railway plan

### Debug Mode

**Enable verbose logging:**
```bash
# Temporary (in Railway terminal)
LOG_LEVEL=DEBUG

# Check logs
railway logs
```

**Test database connection:**
```bash
# In Railway terminal
python init_db.py check
```

**Test API locally:**
```bash
# Use production DATABASE_URL locally (be careful!)
export DATABASE_URL=<production-url>
export REDIS_URL=<production-url>
python -m uvicorn main:app --reload
```

## 📈 Scaling

### Backend Scaling

**Railway (Horizontal Scaling):**
1. Go to Settings → Service → Replicas
2. Increase replica count
3. Railway will load balance automatically

**Optimize Performance:**
- Enable Redis caching (v1.3.0+)
- Use connection pooling (built into SQLAlchemy)
- Optimize database queries (run `optimize_db.py`)
- Increase Railway plan for more resources

### Database Scaling

**Neon:**
- Upgrade to paid plan for more storage
- Use read replicas for read-heavy workloads

**Connection Pooling:**
- Already configured in SQLAlchemy
- Max pool size: 20 connections
- Overflow: 10 connections

### Frontend Scaling

Vercel automatically scales:
- Global CDN edge caching
- Automatic code splitting
- Image optimization
- No configuration needed

## 💰 Cost Estimate

### Free Tier (Good for development/testing)
- **Vercel:** Free (Hobby plan)
- **Railway:** $5/month credit
- **Neon:** Free (0.5 GB)
- **Upstash:** Free (10K requests/day)
- **Total:** $0-5/month

### Production (Small-medium traffic)
- **Vercel:** $20/month (Pro plan)
- **Railway:** $10-20/month (usage-based)
- **Neon:** $19/month (Pro plan - 10 GB)
- **Upstash:** $10/month (Pay as you go)
- **Domain:** $10-15/year
- **Total:** $60-70/month

### High Traffic
- **Vercel:** $20/month+ (based on usage)
- **Railway:** $50-100/month
- **Neon:** $69/month (Scale plan)
- **Upstash:** $30-50/month
- **Sentry:** $26/month
- **Total:** $200-300/month

## 🔐 Backup Strategy

### Database Backups

**Neon (Automatic):**
- Point-in-time recovery (7-30 days depending on plan)
- No configuration needed

**Manual Backup:**
```bash
# Export database
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

**Automated Backups (Railway):**
```bash
# Add to Railway Cron Jobs
0 2 * * * pg_dump $DATABASE_URL | gzip > /backups/backup-$(date +\%Y\%m\%d).sql.gz
```

### Code Backups

- GitHub repository (primary)
- Railway and Vercel deployment history
- Local git repository

## 📝 Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Security review completed
- [ ] Environment variables documented
- [ ] Database migrations tested
- [ ] API endpoints tested
- [ ] Frontend build successful
- [ ] CORS configured correctly
- [ ] SSL certificates configured
- [ ] Monitoring setup
- [ ] Backup strategy in place

### Post-Deployment

- [ ] Health check endpoint responding
- [ ] Frontend loads correctly
- [ ] User registration works
- [ ] User login works
- [ ] Job search works
- [ ] AI matching works
- [ ] Crawlers running on schedule
- [ ] Email notifications working (if configured)
- [ ] Error tracking configured
- [ ] Metrics being collected
- [ ] DNS records propagated
- [ ] SSL certificates active

### First Week Monitoring

- [ ] Monitor error rates
- [ ] Check crawler success rates
- [ ] Review slow requests
- [ ] Monitor database performance
- [ ] Check cache hit rates
- [ ] Review user feedback
- [ ] Monitor costs

## 🆘 Support

### Getting Help

1. **Check Logs:**
   - Railway: Dashboard → Deployments → Logs
   - Vercel: Dashboard → Deployments → Function Logs

2. **Review Documentation:**
   - [Railway Docs](https://docs.railway.app)
   - [Vercel Docs](https://vercel.com/docs)
   - [Next.js Docs](https://nextjs.org/docs)
   - [FastAPI Docs](https://fastapi.tiangolo.com)

3. **Common Resources:**
   - GitHub Issues
   - Stack Overflow
   - Discord/Slack communities

### Rollback Procedure

**Frontend (Vercel):**
1. Go to Deployments tab
2. Find last working deployment
3. Click "..." → "Promote to Production"

**Backend (Railway):**
1. Go to Deployments tab
2. Find last working deployment
3. Click "Redeploy"

**Database:**
```bash
# Rollback migration
python migrate_db.py downgrade
```

## 📄 License

MIT License - See [LICENSE](../LICENSE) file

---

**Version:** 1.10.0
**Last Updated:** 2024-12-19
**Maintainer:** UN Jobs Hub Team
