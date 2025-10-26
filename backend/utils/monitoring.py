"""Performance monitoring and logging utilities."""
import time
import logging
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .logger import set_request_context, clear_request_context

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor API performance and log metrics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add timing and logging to each request."""
        # Start timer
        start_time = time.time()

        # Get method and path
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"

        # Process request
        response = None
        try:
            response = await call_next(request)
            elapsed = (time.time() - start_time) * 1000

            # Log with structured data
            logger.info(
                f"{method} {path} - {response.status_code} - {elapsed:.2f}ms",
                extra={
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "elapsed_ms": round(elapsed, 2),
                    "client_host": client_host
                }
            )

            # Log slow requests (over 1 second)
            if elapsed > 1000:
                logger.warning(
                    f"Slow request detected: {method} {path} took {elapsed:.2f}ms",
                    extra={
                        "method": method,
                        "path": path,
                        "elapsed_ms": round(elapsed, 2),
                        "slow_request": True
                    }
                )

            return response
        except Exception as e:
            # Log error with structured data
            elapsed = (time.time() - start_time) * 1000
            logger.error(
                f"{method} {path} - Error: {str(e)} - {elapsed:.2f}ms",
                extra={
                    "method": method,
                    "path": path,
                    "elapsed_ms": round(elapsed, 2),
                    "client_host": client_host,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            raise


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to each request for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]

        # Add to request state
        request.state.request_id = request_id

        # Set request context for logging
        set_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else "unknown"
        )

        try:
            # Process request
            response = await call_next(request)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response
        finally:
            # Clear request context
            clear_request_context()


def setup_monitoring(app):
    """Set up monitoring and logging for the application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add middleware
    app.add_middleware(PerformanceMonitoringMiddleware)
    app.add_middleware(RequestIDMiddleware)
    
    logger.info("Monitoring and logging configured successfully")

