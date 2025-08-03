from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
import logging
from typing import Optional
from app.src.config.settings import settings

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_EXPIRE_TIME = 3600  # 1 hour in seconds
CACHE_KEY_PREFIX = "analysis"

# Global flag to track if cache is available
_cache_available = False

async def init_cache():
    """Initialize the cache with Redis backend."""
    global _cache_available
    
    try:
        # Check if Redis is enabled via settings
        if not settings.redis_enabled:
            logger.info("Redis cache disabled via settings")
            _cache_available = False
            return
        
        # Create Redis connection with timeout
        redis = aioredis.from_url(
            "redis://localhost:6379",  # Default Redis URL
            encoding="utf8",
            decode_responses=True,
            socket_connect_timeout=5,  # 5 second timeout
            socket_timeout=5
        )
        
        # Test the connection
        await redis.ping()
        
        # Initialize FastAPI Cache
        FastAPICache.init(RedisBackend(redis), prefix=CACHE_KEY_PREFIX)
        
        _cache_available = True
        logger.info("Cache initialized successfully with Redis backend")
        
    except Exception as e:
        logger.warning(f"Failed to initialize Redis cache: {str(e)}")
        logger.info("Continuing without cache - all requests will be processed directly")
        _cache_available = False

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
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # If cache is not available, just call the function directly
            if not _cache_available:
                return await func(*args, **kwargs)
            
            # If cache is available, use the cache decorator
            cached_func = cache(expire=expire)(func)
            return await cached_func(*args, **kwargs)
        
        return wrapper
    
    return decorator 