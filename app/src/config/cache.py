from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_EXPIRE_TIME = 3600  # 1 hour in seconds
CACHE_KEY_PREFIX = "analysis"

async def init_cache():
    """Initialize the cache with Redis backend."""
    try:
        # Create Redis connection
        redis = aioredis.from_url(
            "redis://localhost:6379",  # Default Redis URL
            encoding="utf8",
            decode_responses=True
        )
        
        # Initialize FastAPI Cache
        FastAPICache.init(RedisBackend(redis), prefix=CACHE_KEY_PREFIX)
        
        logger.info("Cache initialized successfully with Redis backend")
        
    except Exception as e:
        logger.error(f"Failed to initialize cache: {str(e)}")
        # Fallback to in-memory cache if Redis is not available
        logger.warning("Falling back to in-memory cache")
        FastAPICache.init(RedisBackend(None), prefix=CACHE_KEY_PREFIX)

def get_cache_key(operation: str, regency_id: str, **kwargs) -> str:
    """
    Generate a cache key for analysis operations.
    
    Args:
        operation: The analysis operation (e.g., 'priority_scores', 'heatmap')
        regency_id: The regency ID
        **kwargs: Additional parameters to include in the cache key
    
    Returns:
        A unique cache key string
    """
    # Create a sorted string of additional parameters
    param_str = ""
    if kwargs:
        sorted_params = sorted(kwargs.items())
        param_str = "_" + "_".join(f"{k}_{v}" for k, v in sorted_params)
    
    return f"{operation}_{regency_id}{param_str}"

def analysis_cache(expire: int = CACHE_EXPIRE_TIME):
    """
    Decorator for caching analysis results.
    
    Args:
        expire: Cache expiration time in seconds (default: 1 hour)
    
    Returns:
        Decorated function with caching
    """
    return cache(expire=expire) 