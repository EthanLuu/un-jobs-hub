"""
Security middleware and utilities.

Provides:
- Security headers
- CSRF protection
- XSS protection
- SQL injection prevention
- Request validation
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import re
from typing import List


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Security headers
        security_headers = {
            # Prevent clickjacking
            "X-Frame-Options": "DENY",

            # XSS Protection
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",

            # HSTS (if using HTTPS)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",

            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            ),

            # Referrer Policy
            "Referrer-Policy": "strict-origin-when-cross-origin",

            # Permissions Policy (formerly Feature Policy)
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=()"
            ),
        }

        for header, value in security_headers.items():
            response.headers[header] = value

        return response


class SQLInjectionProtectionMiddleware(BaseHTTPMiddleware):
    """Detect and block potential SQL injection attempts."""

    # Common SQL injection patterns
    SQL_PATTERNS = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
        r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
        r"((\%27)|(\'))union",
        r"exec(\s|\+)+(s|x)p\w+",
    ]

    def __init__(self, app, strict_mode: bool = False):
        super().__init__(app)
        self.strict_mode = strict_mode
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SQL_PATTERNS]

    def check_sql_injection(self, text: str) -> bool:
        """Check if text contains SQL injection patterns."""
        if not text:
            return False

        for pattern in self.patterns:
            if pattern.search(text):
                return True
        return False

    async def dispatch(self, request: Request, call_next) -> Response:
        # Check query parameters
        for param, value in request.query_params.items():
            if self.check_sql_injection(str(value)):
                return Response(
                    content='{"error": "Potential SQL injection detected"}',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    headers={"Content-Type": "application/json"}
                )

        # Check path parameters
        if self.check_sql_injection(str(request.url.path)):
            return Response(
                content='{"error": "Invalid request path"}',
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"Content-Type": "application/json"}
            )

        return await call_next(request)


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize input data."""

    # Maximum sizes
    MAX_QUERY_PARAM_LENGTH = 1000
    MAX_PATH_LENGTH = 500
    MAX_HEADER_LENGTH = 8192

    # Allowed file extensions for upload
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Validate query parameter length
        for param, value in request.query_params.items():
            if len(str(value)) > self.MAX_QUERY_PARAM_LENGTH:
                return Response(
                    content='{"error": "Query parameter too long"}',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    headers={"Content-Type": "application/json"}
                )

        # Validate path length
        if len(request.url.path) > self.MAX_PATH_LENGTH:
            return Response(
                content='{"error": "Request path too long"}',
                status_code=status.HTTP_414_REQUEST_URI_TOO_LONG,
                headers={"Content-Type": "application/json"}
            )

        # Validate headers length
        for header, value in request.headers.items():
            if len(value) > self.MAX_HEADER_LENGTH:
                return Response(
                    content='{"error": "Header too long"}',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    headers={"Content-Type": "application/json"}
                )

        return await call_next(request)


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent XSS and other attacks.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Limit length
    text = text[:max_length]

    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '`', '|', '\n', '\r']
    for char in dangerous_chars:
        text = text.replace(char, '')

    return text.strip()


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, ""


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension."""
    import os
    _, ext = os.path.splitext(filename.lower())
    return ext in allowed_extensions


# Security checklist for deployment
SECURITY_CHECKLIST = """
# Security Deployment Checklist

## Pre-Deployment

- [ ] Change SECRET_KEY to a strong random value
- [ ] Enable HTTPS/TLS for all communications
- [ ] Set DEBUG=False in production
- [ ] Configure proper CORS origins
- [ ] Enable rate limiting
- [ ] Set up database connection pooling
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting

## Database Security

- [ ] Use strong database passwords
- [ ] Limit database user privileges
- [ ] Enable SSL for database connections
- [ ] Regular backups with encryption
- [ ] Monitor for unusual queries

## API Security

- [ ] Implement rate limiting on all endpoints
- [ ] Validate all input data
- [ ] Use parameterized queries (SQLAlchemy ORM)
- [ ] Implement proper authentication
- [ ] Use HTTPS only
- [ ] Add security headers
- [ ] Enable CSRF protection for state-changing operations

## Application Security

- [ ] Keep dependencies up to date
- [ ] Run security audits (safety, bandit)
- [ ] Implement logging and monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure Content Security Policy
- [ ] Implement file upload validation
- [ ] Use secure session management

## Infrastructure Security

- [ ] Keep OS and packages updated
- [ ] Configure firewall (only allow necessary ports)
- [ ] Use non-root user for application
- [ ] Implement DDoS protection
- [ ] Set up intrusion detection
- [ ] Regular security patches

## Monitoring

- [ ] Monitor for suspicious activity
- [ ] Set up alerts for anomalies
- [ ] Log all authentication attempts
- [ ] Track API usage patterns
- [ ] Monitor error rates
"""
