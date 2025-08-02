from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CacheManager:
    """Utility class for managing analysis cache operations."""
    
    @staticmethod
    async def clear_analysis_cache(regency_id: Optional[str] = None):
        """
        Clear analysis cache for a specific regency or all analysis cache.
        
        Args:
            regency_id: Optional regency ID to clear cache for specific regency
        """
        try:
            if regency_id:
                # Clear cache for specific regency
                pattern = f"analysis:*_{regency_id}_*"
                await FastAPICache.clear(namespace=pattern)
                logger.info(f"Cleared analysis cache for regency {regency_id}")
            else:
                # Clear all analysis cache
                await FastAPICache.clear(namespace="analysis:*")
                logger.info("Cleared all analysis cache")
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
    
    @staticmethod
    async def clear_priority_scores_cache(regency_id: Optional[str] = None):
        """
        Clear priority scores cache for a specific regency or all priority scores cache.
        
        Args:
            regency_id: Optional regency ID to clear cache for specific regency
        """
        try:
            if regency_id:
                # Clear cache for specific regency
                pattern = f"analysis:calculate_priority_scores_{regency_id}_*"
                await FastAPICache.clear(namespace=pattern)
                logger.info(f"Cleared priority scores cache for regency {regency_id}")
            else:
                # Clear all priority scores cache
                await FastAPICache.clear(namespace="analysis:calculate_priority_scores_*")
                logger.info("Cleared all priority scores cache")
                
        except Exception as e:
            logger.error(f"Failed to clear priority scores cache: {str(e)}")
    
    @staticmethod
    async def clear_heatmap_cache(regency_id: Optional[str] = None):
        """
        Clear heatmap cache for a specific regency or all heatmap cache.
        
        Args:
            regency_id: Optional regency ID to clear cache for specific regency
        """
        try:
            if regency_id:
                # Clear cache for specific regency
                pattern = f"analysis:generate_heatmap_data_{regency_id}_*"
                await FastAPICache.clear(namespace=pattern)
                logger.info(f"Cleared heatmap cache for regency {regency_id}")
            else:
                # Clear all heatmap cache
                await FastAPICache.clear(namespace="analysis:generate_heatmap_data_*")
                logger.info("Cleared all heatmap cache")
                
        except Exception as e:
            logger.error(f"Failed to clear heatmap cache: {str(e)}")
    
    @staticmethod
    async def get_cache_stats():
        """
        Get cache statistics (if available).
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            # This is a placeholder - actual implementation depends on Redis client
            return {
                "status": "Cache is running",
                "backend": "Redis",
                "prefix": "analysis"
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            return {"status": "Cache error", "error": str(e)} 