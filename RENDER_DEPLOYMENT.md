# Render Backend Deployment Guide

## Quick Start (100% Free)

### 1. Create Render Account
- Go to https://render.com
- Sign up with GitHub (recommended)
- **Free tier includes**:
  - 750 hours/month (enough for 1 always-on service)
  - Automatic deploys from Git
  - Custom domains
  - Free SSL certificates

### 2. Deploy Backend from GitHub

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `EthanLuu/un-jobs-hub`
3. Configure the service:
   - **Name**: `un-jobs-hub-backend`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

### 3. Configure Environment Variables

In the service dashboard, scroll to **Environment** section and add:

**Required Variables:**
```
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_uk4eOdBWc9tn@ep-billowing-poetry-adzqclhh-pooler.c-2.us-east-1.aws.neon.tech/neondb
SECRET_KEY=your_secret_key_here
PYTHON_VERSION=3.11.0
```

**Optional Variables:**
```
ALLOWED_ORIGINS=https://un-jobs-hub.vercel.app
OPENAI_API_KEY=your_openai_key
DEBUG=False
```

### 4. Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies from requirements.txt
   - Start your FastAPI application
   - Give you a URL like: `https://un-jobs-hub-backend.onrender.com`

### 5. Update Frontend Environment Variable

**In Vercel:**
1. Go to frontend project → Settings → Environment Variables
2. Edit `NEXT_PUBLIC_API_URL`:
   ```
   NEXT_PUBLIC_API_URL=https://un-jobs-hub-backend.onrender.com
   ```
3. Redeploy frontend

### 6. Verify Deployment

```bash
curl https://un-jobs-hub-backend.onrender.com/health
```

## Important: Free Tier Limitations

⚠️ **Render Free tier has one major limitation:**

- **Services spin down after 15 minutes of inactivity**
- **First request after spin-down takes 30-60 seconds to wake up**
- This is acceptable for:
  - Personal projects
  - Testing/demos
  - Low-traffic applications

**To keep service always-on:**
- Upgrade to Render's **Starter plan** ($7/month)
- Or use a cron job to ping your API every 10 minutes

### Option: Auto-ping Service (Keep Free Tier Awake)

Add this to your frontend or use a service like **UptimeRobot**:

```javascript
// In your Next.js app, add a cron endpoint
// pages/api/cron.ts
export default async function handler(req, res) {
  // Ping backend every 10 minutes
  await fetch(process.env.NEXT_PUBLIC_API_URL + '/health');
  res.status(200).json({ pinged: true });
}
```

Then use Vercel Cron:
```json
// vercel.json
{
  "crons": [{
    "path": "/api/cron",
    "schedule": "*/10 * * * *"
  }]
}
```

## Configuration Files

Render uses:
- **requirements.txt**: Python dependencies
- **runtime.txt**: Python version (optional, defaults to 3.7)

No additional config files needed! Render auto-detects Python apps.

## Advantages of Render

✅ **True Free Tier**: Can deploy applications, not just databases
✅ **Native FastAPI Support**: Works perfectly with ASGI
✅ **Automatic HTTPS**: Free SSL certificates
✅ **Auto-deploys**: Pushes to main branch auto-deploy
✅ **No Cold Starts** (on paid plan)
✅ **Background Workers**: Can run Celery (paid plan)
✅ **PostgreSQL Included**: Free PostgreSQL database if needed
✅ **Better than Vercel** for Python backends

## Render vs Railway vs Vercel

| Feature | Render (Free) | Railway (Paid) | Vercel |
|---------|---------------|----------------|--------|
| Free App Deployment | ✅ Yes | ❌ No | ⚠️ Limited |
| FastAPI Support | ✅ Excellent | ✅ Excellent | ❌ Poor |
| Always-On (Free) | ❌ Sleeps | N/A | N/A |
| Cold Start | 30-60s | None | 3-5s |
| Background Tasks | ✅ Yes | ✅ Yes | ❌ No |
| Price | Free | $5/mo | Free |

## Troubleshooting

### Service Won't Start
- Check **Logs** tab in Render dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` has all dependencies

### Database Connection Issues
- Use `postgresql+asyncpg://` prefix
- Remove `?sslmode=require` from connection string
- Verify Neon database allows external connections

### Service Sleeping
- Expected on free tier after 15 min inactivity
- First request will take 30-60s to wake up
- Use UptimeRobot or similar to keep awake
- Or upgrade to Starter plan ($7/mo) for always-on

### CORS Errors
- Update `ALLOWED_ORIGINS` in Render to include frontend URL
- Format: `https://un-jobs-hub.vercel.app`

## Cost Comparison

**Render Free:**
- ✅ Free forever
- ⚠️ Service sleeps after 15 min
- 750 hours/month

**Render Starter ($7/month):**
- ✅ Always-on
- ✅ No sleep
- ✅ Faster deployments

**Railway Hobby ($5/month):**
- ✅ Always-on
- ✅ $5 usage credit
- ❌ No free tier

**Vercel (Free):**
- ✅ Free
- ❌ Poor FastAPI support
- ❌ Many limitations

## Recommendation

1. **Start with Render Free** - See if the sleep issue is acceptable
2. **Use UptimeRobot** to ping every 10 min (free)
3. **If you need always-on** - Consider Render Starter ($7/mo)

## Next Steps

After deployment works:

1. **Setup Redis** (Render has free Redis too!)
2. **Setup Celery Worker** (on paid plan)
3. **Monitor Performance** with Render's built-in metrics
4. **Setup Auto-ping** to keep service awake on free tier

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- GitHub Issues: https://github.com/EthanLuu/un-jobs-hub/issues
