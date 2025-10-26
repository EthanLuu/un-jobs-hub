"""Logging configuration and utilities."""
import logging
import sys
from typing import Optional
from pathlib import Path


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup a logger with consistent formatting.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to log to
        format_string: Optional custom format string

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Default format
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )

    formatter = logging.Formatter(format_string)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class LoggerMixin:
    """Mixin to add logging capabilities to classes."""

    @property
    def logger(self) -> logging.Logger:
        """Get or create a logger for this class."""
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return logging.getLogger(name)


def log_execution_time(logger: logging.Logger):
    """Decorator to log function execution time."""
    import functools
    import time

    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"{func.__name__} completed in {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                logger.error(
                    f"{func.__name__} failed after {elapsed:.2f}ms: {str(e)}"
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"{func.__name__} completed in {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                logger.error(
                    f"{func.__name__} failed after {elapsed:.2f}ms: {str(e)}"
                )
                raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
