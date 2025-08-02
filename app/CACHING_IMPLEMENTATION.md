# Caching Implementation

This document describes the caching implementation for expensive analysis operations using `fastapi-cache2` with Redis backend.

## Overview

The caching system is designed to improve performance for expensive PostGIS spatial analysis operations by storing results in Redis cache. This significantly reduces response times for repeated requests.

## Architecture

### Cache Backend
- **Primary**: Redis (recommended for production)
- **Fallback**: In-memory cache (if Redis is unavailable)

### Cache Configuration
- **Prefix**: `analysis`
- **Default TTL**: 1 hour (3600 seconds)
- **Cache Key Format**: `analysis:{operation}_{regency_id}_{parameters}`

## Cached Operations

### 1. Priority Score Calculation
- **Method**: `calculate_priority_scores`
- **Cache Key**: `analysis:calculate_priority_scores_{regency_id}_{service_radius_km}_{gap_weight}_{efficiency_weight}_{vulnerability_weight}`
- **TTL**: 1 hour

### 2. Heatmap Data Generation
- **Method**: `generate_heatmap_data`
- **Cache Key**: `analysis:generate_heatmap_data_{regency_id}`
- **TTL**: 1 hour

## Implementation Details

### Cache Initialization
```python
# In main.py
@app.on_event("startup")
async def startup_event():
    await init_cache()
```

### Cache Decorator Usage
```python
@analysis_cache(expire=3600)  # Cache for 1 hour
async def calculate_priority_scores(self, regency_id, ...):
    # Expensive PostGIS query here
    pass
```

### Cache Key Generation
The cache key includes:
- Operation name
- Regency ID
- All relevant parameters (sorted for consistency)

## API Endpoints

### Cache Management

#### Clear Cache
```
DELETE /api/v1/analysis/cache/clear?regency_id={optional_regency_id}
```

**Parameters:**
- `regency_id` (optional): Clear cache for specific regency only

**Response:**
```json
{
  "message": "Cache cleared successfully",
  "regency_id": "uuid-or-null",
  "cleared_all": true
}
```

#### Get Cache Statistics
```
GET /api/v1/analysis/cache/stats
```

**Response:**
```json
{
  "status": "Cache is running",
  "backend": "Redis",
  "prefix": "analysis"
}
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install fastapi-cache2[redis] redis
```

### 2. Start Redis Server
```bash
# On Windows (if using WSL or Docker)
docker run -d -p 6379:6379 redis:alpine

# On Linux/Mac
redis-server
```

### 3. Environment Variables (Optional)
Add to your `.env` file:
```
REDIS_URL=redis://localhost:6379
CACHE_EXPIRE_TIME=3600
```

## Cache Invalidation

### Automatic Invalidation
- Cache entries expire after 1 hour
- Different parameter combinations create separate cache entries

### Manual Invalidation
- Use the `/cache/clear` endpoint
- Clear specific regency cache or all analysis cache

### When to Clear Cache
- After data updates (new health facilities, population data)
- When analysis parameters change significantly
- During development/testing

## Performance Benefits

### Before Caching
- PostGIS spatial queries: 2-10 seconds
- Complex calculations: 1-5 seconds
- Total response time: 3-15 seconds

### After Caching
- Cache hit: 50-200ms
- Cache miss: 3-15 seconds (first request)
- Subsequent requests: 50-200ms

## Monitoring

### Cache Hit Rate
Monitor cache effectiveness through:
- Response times
- Cache statistics endpoint
- Application logs

### Cache Size
- Monitor Redis memory usage
- Set appropriate TTL values
- Clear cache when needed

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Check if Redis is running
   - Verify Redis URL configuration
   - Fallback to in-memory cache

2. **Cache Not Working**
   - Check cache initialization in startup
   - Verify decorator usage
   - Check cache key generation

3. **Stale Data**
   - Clear cache after data updates
   - Adjust TTL values
   - Use cache invalidation endpoints

### Debug Commands
```bash
# Check Redis status
redis-cli ping

# Monitor Redis operations
redis-cli monitor

# Check cache keys
redis-cli keys "analysis:*"
```

## Best Practices

1. **Cache Key Design**
   - Include all relevant parameters
   - Use consistent parameter ordering
   - Avoid overly specific keys

2. **TTL Management**
   - Balance freshness vs performance
   - Consider data update frequency
   - Use different TTLs for different operations

3. **Cache Invalidation**
   - Clear cache after data updates
   - Provide manual cache clearing endpoints
   - Monitor cache effectiveness

4. **Error Handling**
   - Graceful fallback when cache fails
   - Log cache operations
   - Handle Redis connection issues 