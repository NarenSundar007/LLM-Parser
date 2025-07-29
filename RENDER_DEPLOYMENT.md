# 🚀 Render Deployment Guide

## Prerequisites
1. GitHub account with your code
2. Render account (free at render.com)
3. Groq API key from console.groq.com

## 📋 Step-by-Step Deployment

### 1. Prepare Your Repository
```bash
# Make sure all files are committed
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Deploy on Render

1. **Go to [render.com](https://render.com)** and sign up/login
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub** repository
4. **Configure the service:**
   - **Name:** `bajaj-hackathon-llm-system`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Plan:** `Free`

### 3. Set Environment Variables
In Render dashboard, go to **Environment** and add:

```bash
GROQ_API_KEY=your_actual_groq_api_key_here
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_WORKERS=1
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
USE_PINECONE=false
```

### 4. Add Persistent Storage (Optional)
- Go to **Settings** → **Disks**
- Add disk: `/opt/render/project/src/data` (1GB free)

## 🔧 Render Free Tier Limitations

| Resource | Limit |
|----------|-------|
| RAM | 512MB |
| CPU | 0.1 vCPU |
| Storage | 1GB SSD |
| Bandwidth | 100GB/month |
| Sleep | After 15min inactivity |

## 🎯 Optimizations for Free Tier

### 1. Memory Optimization
- Using CPU-only PyTorch
- Single worker process
- Optimized sentence-transformers model

### 2. Performance Tips
- Service sleeps after 15min → first request may be slow
- Use smaller batch sizes
- Consider using paid tier for production

### 3. Alternative Deployment URLs
After deployment, your API will be available at:
```
https://your-service-name.onrender.com
```

## 🧪 Testing Your Deployment

Update your test script:
```python
# In test_batch_query.py, change the URL:
response = await client.post(
    "https://your-service-name.onrender.com/batch-query",
    json=batch_request
)
```

## 📊 Monitoring

### Health Check
```bash
curl https://your-service-name.onrender.com/health
```

### Logs
Check logs in Render dashboard under **Logs** tab

## 🚨 Troubleshooting

### Common Issues:
1. **Build timeout** → Optimize requirements.txt
2. **Memory errors** → Reduce model size or upgrade plan
3. **Cold starts** → Service sleeps, first request slow

### Quick Fixes:
```bash
# If build fails, try minimal requirements:
fastapi==0.104.1
uvicorn==0.24.0
groq==0.11.0
sentence-transformers==2.2.2
PyMuPDF==1.23.8
```

## 💰 Cost Optimization

### Free Tier Strategy:
- Use for demos and testing
- Implement request caching
- Optimize model loading

### Upgrade Path:
- **Starter Plan:** $7/month (512MB RAM)
- **Standard Plan:** $25/month (2GB RAM)

## 🔄 Auto-Deployment

Enable auto-deployment from your main branch:
1. Go to **Settings**
2. Enable **Auto-Deploy**
3. Push changes to trigger deployment

## 🌐 Custom Domain (Optional)

For production:
1. Go to **Settings** → **Custom Domains**
2. Add your domain
3. Configure DNS records

## 📝 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] requirements.txt optimized
- [ ] Environment variables set
- [ ] Health endpoint working
- [ ] API endpoints tested
- [ ] Logs monitoring setup

## 🎉 Next Steps

1. Test your deployed API
2. Update documentation with new URL
3. Consider setting up monitoring
4. Plan for scaling if needed

Your LLM Query System is now live on Render! 🚀
