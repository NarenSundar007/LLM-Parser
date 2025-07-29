# 🚀 Render Deployment Guide

## Quick Deploy to Render

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Deploy on Render
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Use these settings:

**Basic Settings:**
- **Name**: `bajaj-hackathon-llm-system`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Advanced Settings:**
- **Instance Type**: Free (512MB RAM, 0.1 CPU)
- **Auto-Deploy**: Yes

### 3. Environment Variables
Add these in Render Dashboard → Environment:

```
GROQ_API_KEY=your_groq_api_key_here
ENVIRONMENT=production
```

### 4. Optional: Custom Domain
- Free tier gets: `https://your-app-name.onrender.com`
- Paid plans allow custom domains

## 📁 Persistent Storage

Render free tier includes:
- **Ephemeral storage**: Temporary files (gets reset on deploy)
- **Persistent disk**: For FAISS index (requires paid plan)

For free tier, the FAISS index rebuilds on each deploy (which is fine for demos).

## 🔧 Deployment Files Created

1. **render.yaml** - Render service configuration
2. **requirements.txt** - Python dependencies (updated)
3. **Updated config.py** - Handles PORT environment variable
4. **Updated main.py** - Production-ready startup

## 💰 Render Pricing

**Free Tier:**
- 512MB RAM, 0.1 CPU
- 750 hours/month (enough for hackathon)
- Apps sleep after 15min inactivity
- Perfect for demos and development

**Starter Plan ($7/month):**
- 512MB RAM, 0.5 CPU
- No sleeping
- Custom domains
- Persistent disks

## 🚨 Important Notes

1. **First Deploy**: Takes 5-10 minutes (downloads ML models)
2. **Cold Starts**: Free tier apps sleep, first request may be slow
3. **Memory**: 512MB should be sufficient for your app
4. **API Keys**: Always use environment variables, never commit keys

## 🧪 Testing Your Deployed App

Once deployed, update your test script:

```python
# Update test_batch_query.py
base_url = "https://your-app-name.onrender.com"
```

## 🔄 Alternative Quick Deployment Options

### Railway (Similar to Render)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Docker (For any platform)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE $PORT
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 🎯 Next Steps

1. Deploy to Render using the guide above
2. Test with your batch query endpoint
3. Share the live URL for your Bajaj Hackathon demo!

Your app will be accessible at: `https://bajaj-hackathon-llm-system.onrender.com`
