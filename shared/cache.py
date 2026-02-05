"""
Response caching with Redis for KIKI Agent services
Quick Win #10: Implements TTL-based caching with decorators
"""

import redis.asyncio as aioredis
import json
import hashlib
import logging
from typing import Optional, Callable, Any
from functools import wraps
import asyncio
from datetime import timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis-based cache manager with TTL support.
    Implements cache-aside pattern with automatic serialization.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://redis:6379/0",
        default_ttl: int = 300,
        key_prefix: str = "kiki"
    ):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live in seconds
            key_prefix: Prefix for all cache keys
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Establish Redis connection"""
        if self.redis is None:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50
            )
            logger.info(f"Cache manager connected to Redis: {self.redis_url}")
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Cache manager disconnected from Redis")
    
    def _make_key(self, key: str) -> str:
        """Generate prefixed cache key"""
        return f"{self.key_prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        if not self.redis:
            await self.connect()
        
        cache_key = self._make_key(key)
        try:
            value = await self.redis.get(cache_key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {cache_key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time-to-live in seconds (uses default if None)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            await self.connect()
        
        cache_key = self._make_key(key)
        ttl = ttl or self.default_ttl
        
        try:
            serialized = json.dumps(value)
            await self.redis.setex(cache_key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {cache_key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis:
            await self.connect()
        
        cache_key = self._make_key(key)
        try:
            await self.redis.delete(cache_key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {cache_key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis:
            await self.connect()
        
        cache_key = self._make_key(key)
        try:
            return await self.redis.exists(cache_key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {cache_key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.
        
        Args:
            pattern: Key pattern with wildcards (e.g., "user:*")
        
        Returns:
            Number of keys deleted
        """
        if not self.redis:
            await self.connect()
        
        full_pattern = self._make_key(pattern)
        try:
            keys = []
            async for key in self.redis.scan_iter(match=full_pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Invalidated {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation error for pattern {pattern}: {e}")
            return 0


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def init_cache(
    redis_url: str = "redis://redis:6379/0",
    default_ttl: int = 300,
    key_prefix: str = "kiki"
) -> CacheManager:
    """Initialize global cache manager"""
    global _cache_manager
    if _cache_manager is not None:
        logger.warning("Cache manager already initialized")
        return _cache_manager
    
    _cache_manager = CacheManager(
        redis_url=redis_url,
        default_ttl=default_ttl,
        key_prefix=key_prefix
    )
    return _cache_manager


def get_cache() -> CacheManager:
    """Get global cache manager instance"""
    if _cache_manager is None:
        raise RuntimeError("Cache manager not initialized. Call init_cache() first.")
    return _cache_manager


def cached(
    ttl: int = 300,
    key_prefix: str = "",
    skip_cache: Callable[[Any], bool] = None
):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Additional prefix for cache key
        skip_cache: Optional function to determine if cache should be skipped
    
    Usage:
        @cached(ttl=600, key_prefix="user")
        async def get_user_profile(user_id: str):
            # ... expensive operation
            return user_data
        
        # Cache key will be: kiki:user:get_user_profile:arg1:arg2...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__] if key_prefix else [func.__name__]
            
            # Add positional arguments to key
            for arg in args:
                key_parts.append(str(arg))
            
            # Add keyword arguments to key (sorted for consistency)
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
            
            cache_key = ":".join(key_parts)
            
            # Check if we should skip cache
            if skip_cache and skip_cache(*args, **kwargs):
                return await func(*args, **kwargs)
            
            # Try to get from cache
            cache = get_cache()
            cached_value = await cache.get(cache_key)
            
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value
            
            # Cache miss - execute function
            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator


def cache_invalidate(pattern: str):
    """
    Decorator to invalidate cache after function execution.
    
    Usage:
        @cache_invalidate(pattern="user:*")
        async def update_user(user_id: str, data: dict):
            # ... update user
            return updated_user
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Invalidate cache after successful execution
            cache = get_cache()
            await cache.invalidate_pattern(pattern)
            
            return result
        return wrapper
    return decorator
