"""Custom exceptions and error handlers."""
from typing import Any, Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class UNJobsException(Exception):
    """Base exception for UN Jobs Hub."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(UNJobsException):
    """Database related exceptions."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class CrawlerException(UNJobsException):
    """Web crawler related exceptions."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class NotFoundException(UNJobsException):
    """Resource not found exception."""

    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            message=f"{resource} with id {resource_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "id": resource_id}
        )


class ValidationException(UNJobsException):
    """Validation exception."""

    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class AuthenticationException(UNJobsException):
    """Authentication exception."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(UNJobsException):
    """Authorization exception."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


async def unjobs_exception_handler(
    request: Request,
    exc: UNJobsException
) -> JSONResponse:
    """Handle custom UNJobs exceptions."""
    logger.error(
        f"UNJobs Exception: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "path": str(request.url.path)
        }
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.warning(
        f"HTTP Exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": str(request.url.path)
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation exceptions."""
    logger.warning(
        f"Validation Error: {exc.errors()}",
        extra={"path": request.url.path}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "path": str(request.url.path)
        }
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """Handle SQLAlchemy exceptions."""
    logger.error(
        f"Database Error: {str(exc)}",
        extra={"path": request.url.path},
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database error occurred",
            "path": str(request.url.path)
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle all other exceptions."""
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        extra={"path": request.url.path},
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )


def setup_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    from fastapi.exceptions import RequestValidationError
    from sqlalchemy.exc import SQLAlchemyError

    app.add_exception_handler(UNJobsException, unjobs_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
