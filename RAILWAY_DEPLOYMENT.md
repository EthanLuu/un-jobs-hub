# Railway Backend Deployment Guide

## Quick Start

### 1. Create Railway Account
- Go to https://railway.app
- Sign up with GitHub (recommended)
- Railway offers $5 free credit per month

### 2. Deploy Backend from GitHub

#### Option A: Using Railway Dashboard (Recommended)
1. Click "New Project" on Railway dashboard
2. Select "Deploy from GitHub repo"
3. Choose your repository: `EthanLuu/un-jobs-hub`
4. Railway will ask which directory to deploy:
   - Select **Root Directory** and set **Root Path** to `/backend`
   - Or manually set the working directory to `backend`

#### Option B: Using Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Navigate to backend directory
cd backend

# Initialize and deploy
railway init
railway up
```

### 3. Configure Environment Variables

In Railway dashboard, go to your service → Variables → Add the following:

**Required Variables:**
```
DATABASE_URL=your_neon_database_url
SECRET_KEY=your_secret_key_here
REDIS_URL=redis://default:password@redis.railway.internal:6379
```

**Optional Variables:**
```
ALLOWED_ORIGINS=https://un-jobs-hub.vercel.app
OPENAI_API_KEY=your_openai_key
DEBUG=False
```

**Important Notes:**
- Railway automatically provides `PORT` environment variable
- For DATABASE_URL, use your Neon connection string:
  ```
  postgresql+asyncpg://neondb_owner:password@ep-xxxx.aws.neon.tech/neondb
  ```
- Don't include `?sslmode=require` in the URL (handled in code)

### 4. Add Redis (Optional, for caching and Celery)

1. In Railway project, click "New" → "Database" → "Add Redis"
2. Railway will automatically set `REDIS_URL` environment variable
3. Copy the internal Redis URL to your backend service variables

### 5. Get Your API URL

After deployment:
1. Go to your backend service in Railway
2. Click "Settings" → "Generate Domain"
3. Railway will give you a URL like: `https://un-jobs-hub-backend-production.up.railway.app`
4. Copy this URL

### 6. Update Frontend Environment Variable

**In Vercel:**
1. Go to your frontend project settings
2. Environment Variables → Edit `NEXT_PUBLIC_API_URL`
3. Change from Vercel backend URL to Railway URL:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app
   ```
4. Redeploy frontend

**In Local Development:**
Update `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app
```

### 7. Verify Deployment

Test your API:
```bash
curl https://your-railway-url.up.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

## Configuration Files

Railway uses these files for deployment:

- **railway.json**: Railway-specific configuration
- **Procfile**: Tells Railway how to start the application
- **runtime.txt**: Specifies Python version
- **requirements.txt**: Python dependencies

## Advantages of Railway vs Vercel

✅ **Better FastAPI Support**: Native ASGI support
✅ **No Timeout Limits**: Can run long-running requests
✅ **Persistent Connections**: Better for database connections
✅ **Background Workers**: Can run Celery workers
✅ **WebSocket Support**: If needed in the future
✅ **Better Logging**: More detailed logs and metrics
✅ **No Cold Starts**: Always-on instances (with paid plan)

## Troubleshooting

### Build Fails
- Check build logs in Railway dashboard
- Ensure `requirements.txt` has all dependencies
- Verify Python version in `runtime.txt`

### Database Connection Issues
- Ensure DATABASE_URL uses `postgresql+asyncpg://`
- Remove `?sslmode=require` from connection string
- Check Neon database is accessible from Railway IPs

### Port Binding Issues
- Railway automatically sets `PORT` environment variable
- Our Procfile uses `--port $PORT` to bind correctly

### CORS Errors
- Update `ALLOWED_ORIGINS` in Railway to include your frontend URL
- Format: `https://un-jobs-hub.vercel.app,https://localhost:3000`

## Cost Estimate

**Free Tier:**
- $5 credit per month
- ~500 hours of usage
- Perfect for development/testing

**Pro Plan ($20/month):**
- Unlimited projects
- Better performance
- Priority support

## Next Steps

After basic deployment works:

1. **Setup Celery Worker** (for job crawling):
   - Add another service in Railway project
   - Use start command: `celery -A celery_app worker --loglevel=info`
   - Share same environment variables

2. **Setup Celery Beat** (for scheduled tasks):
   - Add another service
   - Use start command: `celery -A celery_app beat --loglevel=info`

3. **Monitor Performance**:
   - Use Railway's built-in metrics
   - Check response times and memory usage

4. **Setup Alerts**:
   - Configure Railway notifications
   - Get notified of deployment failures

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/EthanLuu/un-jobs-hub/issues
