"""Logging configuration and utilities."""
import logging
import sys
import json
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from contextvars import ContextVar

# Context variable for request tracking
request_context: ContextVar[Dict[str, Any]] = ContextVar('request_context', default={})


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'message', 'pathname', 'process', 'processName',
                'relativeCreated', 'thread', 'threadName', 'exc_info',
                'exc_text', 'stack_info'
            ]:
                log_data[key] = value

        # Add context data if available
        context = request_context.get()
        if context:
            log_data['context'] = context

        return json.dumps(log_data)


class StructuredLogger(logging.Logger):
    """Logger with structured logging support."""

    def _log_structured(
        self,
        level: int,
        msg: Any,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
        **kwargs
    ):
        """Log with structured data."""
        if extra is None:
            extra = {}
        extra.update(kwargs)
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel + 1)

    def info_structured(self, msg: str, **kwargs):
        """Log info with structured data."""
        self._log_structured(logging.INFO, msg, (), **kwargs)

    def error_structured(self, msg: str, **kwargs):
        """Log error with structured data."""
        self._log_structured(logging.ERROR, msg, (), **kwargs)

    def warning_structured(self, msg: str, **kwargs):
        """Log warning with structured data."""
        self._log_structured(logging.WARNING, msg, (), **kwargs)

    def debug_structured(self, msg: str, **kwargs):
        """Log debug with structured data."""
        self._log_structured(logging.DEBUG, msg, (), **kwargs)


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
    json_format: bool = False,
    use_structured: bool = False
) -> logging.Logger:
    """
    Setup a logger with consistent formatting.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to log to
        format_string: Optional custom format string
        json_format: Use JSON formatting for structured logging
        use_structured: Return a StructuredLogger instance

    Returns:
        Configured logger instance
    """
    # Use StructuredLogger if requested
    if use_structured:
        logging.setLoggerClass(StructuredLogger)

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Choose formatter based on json_format
    if json_format:
        formatter = JSONFormatter()
    else:
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

    # Reset logger class
    if use_structured:
        logging.setLoggerClass(logging.Logger)

    return logger


def set_request_context(**kwargs):
    """Set context data for the current request."""
    context = request_context.get().copy()
    context.update(kwargs)
    request_context.set(context)


def clear_request_context():
    """Clear request context data."""
    request_context.set({})


class log_context:
    """Context manager for adding context data to logs."""

    def __init__(self, **kwargs):
        self.context_data = kwargs
        self.old_context = None

    def __enter__(self):
        self.old_context = request_context.get().copy()
        new_context = self.old_context.copy()
        new_context.update(self.context_data)
        request_context.set(new_context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        request_context.set(self.old_context)


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
