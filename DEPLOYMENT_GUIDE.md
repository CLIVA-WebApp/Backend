# Vercel Deployment Guide

This guide explains how to deploy the CLIVA Health Planning Platform to Vercel serverless functions.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install with `npm i -g vercel`
3. **Git Repository**: Your code should be in a Git repository

## Deployment Steps

### 1. Prepare Your Environment

Ensure your environment variables are ready for production:

```bash
# Copy your .env file and update for production
cp .env .env.production
```

### 2. Set Environment Variables in Vercel

You'll need to set these environment variables in your Vercel dashboard:

```env
# Supabase Configuration
SUPABASE_USER=your-supabase-user
SUPABASE_PASSWORD=your-supabase-password
SUPABASE_HOST=your-project.supabase.co
SUPABASE_PORT=5432
SUPABASE_DBNAME=postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Groq AI API
GROQ_API_KEY=your-groq-api-key

# App URLs (Update these for your Vercel domain)
FRONTEND_URL=https://your-frontend-domain.vercel.app
BACKEND_URL=https://your-backend-domain.vercel.app
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

### 3. Deploy to Vercel

#### Option A: Using Vercel CLI

```bash
# Navigate to the Backend directory
cd Backend

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts:
# - Link to existing project or create new
# - Set project name
# - Set build command (leave empty for auto-detection)
# - Set output directory (leave empty for auto-detection)
```

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your Git repository
4. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: `Backend`
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty

### 4. Configure Environment Variables

In your Vercel project dashboard:

1. Go to **Settings** → **Environment Variables**
2. Add each environment variable from the list above
3. Set the environment to **Production** (and optionally **Preview**)

### 5. Test Deployment Setup

Before deploying, test your setup:

```bash
# Test deployment configuration
python test_deployment.py
```

### 6. Deploy

```bash
# Deploy to production
vercel --prod

# Or deploy from dashboard by pushing to main branch
git push origin main
```

## Configuration Files

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/src/main.py",
      "use": "@vercel/python@3.1.0"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/src/main.py"
    }
  ],
  "env": {
    "PYTHONPATH": "."
  },
  "functions": {
    "app/src/main.py": {
      "maxDuration": 300
    }
  }
}
```

### requirements.txt
Production dependencies for Vercel deployment (excludes geospatial libraries for compatibility).

### requirements-dev.txt
Development dependencies including geospatial libraries (geopandas, fiona, shapely).

### runtime.txt
Specifies Python 3.12 for the deployment.



## Serverless Considerations

### ✅ Compatible Features
- **API Endpoints**: All REST endpoints work perfectly
- **Database Operations**: Supabase cloud database works great
- **Authentication**: JWT and OAuth work seamlessly
- **CORS**: Properly configured for frontend integration

### ⚠️ Limitations & Solutions

#### 1. File System Operations
**Issue**: Serverless functions have read-only filesystem
**Solution**: 
- Use cloud storage (AWS S3, Supabase Storage) for file uploads
- Generate reports in memory and return as download
- Use external services for file processing

#### 2. Long-Running Operations
**Issue**: Vercel has 300-second timeout for all plans
**Solution**:
- Break complex operations into smaller chunks
- Use background jobs for heavy processing
- Optimize algorithms for faster execution

#### 3. Memory Limitations
**Issue**: Serverless functions have memory limits
**Solution**:
- Optimize imports and dependencies
- Use streaming for large data processing
- Implement pagination for large datasets

## Performance Optimization

### 1. Cold Start Optimization
```python
# Use lazy imports in main.py
from app.src.config.settings import settings
from app.src.config.cache import init_cache

# Initialize heavy components on first request
_cache_initialized = False

@app.middleware("http")
async def initialize_cache(request: Request, call_next):
    global _cache_initialized
    if not _cache_initialized:
        await init_cache()
        _cache_initialized = True
    return await call_next(request)
```

### 2. Database Connection Pooling
```python
# In database.py
from sqlalchemy.pool import StaticPool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=300,
)
```

### 3. Caching Strategy
```python
# Use Redis for caching (if available)
# Fallback to in-memory cache for serverless
if REDIS_URL:
    cache = RedisCache()
else:
    cache = InMemoryCache()
```

## Monitoring & Debugging

### 1. Vercel Analytics
- Monitor function execution times
- Track error rates
- Analyze cold start performance

### 2. Logging
```python
import logging

# Configure logging for Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {"status": "healthy"}
```

### 3. Error Tracking
- Integrate with Sentry for error tracking
- Use Vercel's built-in error monitoring
- Set up alerts for critical failures

## Custom Domain Setup

1. **Add Custom Domain**:
   - Go to Vercel dashboard → Settings → Domains
   - Add your custom domain
   - Update DNS records as instructed

2. **Update Environment Variables**:
   ```env
   BACKEND_URL=https://api.yourdomain.com
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Check Python path
   echo $PYTHONPATH
   
   # Verify requirements.txt
   pip install -r requirements.txt
   ```

2. **Environment Variables Not Loading**
   ```bash
   # Check in Vercel dashboard
   # Verify variable names and values
   ```

3. **Database Connection Issues**
   ```bash
   # Test Supabase connection
   # Verify credentials in Vercel dashboard
   ```

4. **Timeout Errors**
   ```bash
   # Check function duration
   # Optimize slow operations
   # Consider upgrading plan
   ```

### Debug Commands

```bash
# Test locally with Vercel dev
vercel dev

# Check deployment status
vercel ls

# View function logs
vercel logs

# Redeploy specific function
vercel --prod
```

## Cost Optimization

### 1. Function Optimization
- Minimize cold starts
- Optimize bundle size
- Use efficient algorithms

### 2. Database Optimization
- Use connection pooling
- Implement caching
- Optimize queries

### 3. Monitoring Usage
- Track function invocations
- Monitor execution times
- Set up usage alerts

## Security Considerations

### 1. Environment Variables
- Never commit secrets to Git
- Use Vercel's secure environment variables
- Rotate keys regularly

### 2. API Security
- Implement rate limiting
- Use HTTPS only
- Validate all inputs

### 3. Database Security
- Use connection pooling
- Implement proper authentication
- Regular security audits

## Next Steps

1. **Deploy to Production**: Follow the deployment steps above
2. **Set Up Monitoring**: Configure logging and error tracking
3. **Optimize Performance**: Monitor and optimize based on usage
4. **Scale as Needed**: Upgrade Vercel plan if required

---

**For more information, see the main [README.md](./README.md) and [TECHNICAL_README.md](./TECHNICAL_README.md)** 