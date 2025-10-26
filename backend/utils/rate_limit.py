"""Rate limiting middleware and utilities."""
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class InMemoryRateLimiter:
    """In-memory rate limiter using sliding window algorithm."""

    def __init__(self):
        # Structure: {identifier: [(timestamp, count), ...]}
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is allowed based on rate limit.

        Args:
            identifier: Unique identifier (e.g., IP address, user ID)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, info_dict)
        """
        now = time.time()
        window_start = now - window_seconds

        # Clean old requests
        self.requests[identifier] = [
            (ts, count) for ts, count in self.requests[identifier]
            if ts > window_start
        ]

        # Count requests in current window
        current_requests = sum(count for _, count in self.requests[identifier])

        # Check if allowed
        is_allowed = current_requests < max_requests

        if is_allowed:
            # Add current request
            self.requests[identifier].append((now, 1))

        # Calculate reset time
        reset_time = int(now + window_seconds)

        info = {
            "limit": max_requests,
            "remaining": max(0, max_requests - current_requests - (1 if is_allowed else 0)),
            "reset": reset_time,
            "current": current_requests + (1 if is_allowed else 0)
        }

        return is_allowed, info

    def cleanup(self, max_age_seconds: int = 3600):
        """Remove old entries to prevent memory leaks."""
        cutoff = time.time() - max_age_seconds

        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                (ts, count) for ts, count in self.requests[identifier]
                if ts > cutoff
            ]
            if not self.requests[identifier]:
                del self.requests[identifier]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI.

    Supports both global and per-endpoint rate limits.
    """

    def __init__(
        self,
        app,
        default_limit: int = 100,
        default_window: int = 60,
        enable_cleanup: bool = True,
        cleanup_interval: int = 3600
    ):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            default_limit: Default max requests per window
            default_window: Default window size in seconds
            enable_cleanup: Enable periodic cleanup
            cleanup_interval: Cleanup interval in seconds
        """
        super().__init__(app)
        self.limiter = InMemoryRateLimiter()
        self.default_limit = default_limit
        self.default_window = default_window
        self.last_cleanup = time.time()
        self.cleanup_interval = cleanup_interval
        self.enable_cleanup = enable_cleanup

        # Custom limits for specific endpoints
        self.custom_limits = {
            "/api/auth/login": (5, 300),  # 5 requests per 5 minutes
            "/api/auth/register": (3, 3600),  # 3 requests per hour
            "/api/match": (10, 60),  # 10 requests per minute
        }

    def get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting."""
        # Try to get user ID from request state (set by auth middleware)
        user = getattr(request.state, "user", None)
        if user:
            return f"user:{user.id}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

    def get_limit(self, path: str) -> Tuple[int, int]:
        """Get rate limit for specific path."""
        # Check for custom limits
        for pattern, (limit, window) in self.custom_limits.items():
            if path.startswith(pattern):
                return limit, window

        return self.default_limit, self.default_window

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for health check
        if request.url.path in ["/health", "/api/health", "/"]:
            return await call_next(request)

        # Periodic cleanup
        if self.enable_cleanup:
            now = time.time()
            if now - self.last_cleanup > self.cleanup_interval:
                self.limiter.cleanup()
                self.last_cleanup = now

        # Get rate limit parameters
        identifier = self.get_identifier(request)
        max_requests, window = self.get_limit(request.url.path)

        # Check rate limit
        is_allowed, info = self.limiter.is_allowed(
            identifier,
            max_requests,
            window
        )

        # Add rate limit headers
        headers = {
            "X-RateLimit-Limit": str(info["limit"]),
            "X-RateLimit-Remaining": str(info["remaining"]),
            "X-RateLimit-Reset": str(info["reset"]),
        }

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {identifier} on {request.url.path}",
                extra={
                    "identifier": identifier,
                    "path": request.url.path,
                    "current": info["current"],
                    "limit": info["limit"]
                }
            )

            return Response(
                content='{"error": "Rate limit exceeded", "retry_after": %d}' % (
                    info["reset"] - int(time.time())
                ),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    **headers,
                    "Retry-After": str(info["reset"] - int(time.time())),
                    "Content-Type": "application/json"
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value

        return response


def rate_limit_decorator(max_requests: int, window_seconds: int):
    """
    Decorator for route-specific rate limiting.

    Usage:
        @app.get("/api/expensive")
        @rate_limit_decorator(10, 60)
        async def expensive_endpoint():
            pass
    """
    def decorator(func):
        # This is a placeholder - actual implementation would require
        # integration with the middleware or a dependency
        func._rate_limit = (max_requests, window_seconds)
        return func
    return decorator


# Example usage configuration
class RateLimitConfig:
    """Rate limit configuration presets."""

    # Strict limits for authentication endpoints
    AUTH_STRICT = (5, 300)  # 5 requests per 5 minutes

    # Standard API limits
    API_STANDARD = (100, 60)  # 100 requests per minute

    # Generous limits for read-only endpoints
    API_GENEROUS = (1000, 60)  # 1000 requests per minute

    # Tight limits for expensive operations
    API_EXPENSIVE = (10, 60)  # 10 requests per minute

    # Public endpoints
    PUBLIC = (60, 60)  # 60 requests per minute
