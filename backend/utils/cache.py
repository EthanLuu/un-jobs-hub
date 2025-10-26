"""Redis caching utilities."""
import json
import pickle
from typing import Any, Optional, Callable
from functools import wraps
import logging
from redis import Redis
from redis.exceptions import RedisError
from config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager with fallback to no-cache."""

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize cache manager.

        Args:
            redis_url: Redis connection URL (defaults to settings)
        """
        self.redis_url = redis_url or settings.redis_url
        self._client: Optional[Redis] = None
        self._enabled = bool(self.redis_url)

        if self._enabled:
            try:
                self._client = Redis.from_url(
                    self.redis_url,
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
                # Test connection
                self._client.ping()
                logger.info("Redis cache initialized successfully")
            except RedisError as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self._enabled = False
                self._client = None

    @property
    def is_enabled(self) -> bool:
        """Check if cache is enabled and connected."""
        return self._enabled and self._client is not None

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        if not self.is_enabled:
            return default

        try:
            value = self._client.get(key)
            if value is None:
                return default

            # Try to unpickle
            try:
                return pickle.loads(value)
            except (pickle.PickleError, TypeError):
                # Fall back to string
                return value.decode('utf-8') if isinstance(value, bytes) else value

        except RedisError as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = no expiration)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled:
            return False

        try:
            # Pickle complex objects
            if not isinstance(value, (str, bytes, int, float)):
                value = pickle.dumps(value)
            elif isinstance(value, str):
                value = value.encode('utf-8')

            if ttl:
                self._client.setex(key, ttl, value)
            else:
                self._client.set(key, value)

            return True

        except (RedisError, pickle.PickleError) as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.is_enabled:
            return False

        try:
            self._client.delete(key)
            return True
        except RedisError as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Pattern to match (e.g., 'jobs:*')

        Returns:
            Number of keys deleted
        """
        if not self.is_enabled:
            return 0

        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0

    def get_json(self, key: str, default: Any = None) -> Any:
        """Get JSON value from cache."""
        value = self.get(key)
        if value is None:
            return default

        try:
            if isinstance(value, (bytes, str)):
                return json.loads(value)
            return value
        except json.JSONDecodeError:
            logger.error(f"JSON decode error for key {key}")
            return default

    def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set JSON value in cache."""
        try:
            json_str = json.dumps(value)
            return self.set(key, json_str, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encode error for key {key}: {e}")
            return False

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter."""
        if not self.is_enabled:
            return None

        try:
            return self._client.incr(key, amount)
        except RedisError as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.is_enabled:
            return False

        try:
            return bool(self._client.exists(key))
        except RedisError as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False


# Global cache instance
cache = CacheManager()


def cached(
    ttl: int = 300,
    key_prefix: str = "",
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching function results.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        key_builder: Custom function to build cache key

    Usage:
        @cached(ttl=300, key_prefix="jobs")
        async def get_jobs(limit: int = 10):
            return await fetch_jobs(limit)

        # Will cache with key: "jobs:10"
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default: use function name and args
                args_str = "_".join(str(arg) for arg in args)
                kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                parts = [key_prefix or func.__name__, args_str, kwargs_str]
                cache_key = ":".join(filter(None, parts))

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value

            # Execute function
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, ttl)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                args_str = "_".join(str(arg) for arg in args)
                kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                parts = [key_prefix or func.__name__, args_str, kwargs_str]
                cache_key = ":".join(filter(None, parts))

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value

            # Execute function
            logger.debug(f"Cache miss for {cache_key}")
            result = func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, ttl)

            return result

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Cache key builders for common patterns
class CacheKeys:
    """Standard cache key patterns."""

    @staticmethod
    def job(job_id: int) -> str:
        """Cache key for single job."""
        return f"job:{job_id}"

    @staticmethod
    def jobs_list(page: int = 1, **filters) -> str:
        """Cache key for job list."""
        filter_str = "_".join(f"{k}={v}" for k, v in sorted(filters.items()) if v)
        return f"jobs:page={page}:{filter_str}"

    @staticmethod
    def user(user_id: int) -> str:
        """Cache key for user."""
        return f"user:{user_id}"

    @staticmethod
    def metrics() -> str:
        """Cache key for metrics."""
        return "metrics:global"
