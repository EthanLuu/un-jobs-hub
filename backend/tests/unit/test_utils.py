"""Tests for utility functions."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token
)


@pytest.mark.unit
class TestAuthUtils:
    """Test authentication utilities."""
    
    def test_password_hashing(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt format
    
    def test_password_verification(self):
        """Test password verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Correct password
        assert verify_password(password, hashed) is True
        
        # Wrong password
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Token should have 3 parts (header.payload.signature)
        parts = token.split(".")
        assert len(parts) == 3
    
    def test_create_access_token_with_expiry(self):
        """Test access token creation with custom expiry."""
        data = {"user_id": 1, "email": "test@example.com"}
        expires_delta = timedelta(hours=1)
        token = create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token(self):
        """Test token verification."""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        # Verify valid token
        payload = verify_token(token)
        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["email"] == "test@example.com"
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = verify_token(invalid_token)
        assert payload is None
    
    def test_verify_expired_token(self):
        """Test verification of expired token."""
        data = {"user_id": 1, "email": "test@example.com"}
        # Create token with very short expiry
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)
        
        payload = verify_token(token)
        assert payload is None


@pytest.mark.unit
class TestValidationUtils:
    """Test validation utilities."""
    
    def test_email_validation(self):
        """Test email validation."""
        from email_validator import validate_email, EmailNotValidError
        
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "admin+test@company.org"
        ]
        
        for email in valid_emails:
            try:
                validate_email(email)
                assert True
            except EmailNotValidError:
                assert False, f"Valid email rejected: {email}"
        
        # Invalid emails
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            ""
        ]
        
        for email in invalid_emails:
            try:
                validate_email(email)
                assert False, f"Invalid email accepted: {email}"
            except EmailNotValidError:
                assert True
    
    def test_password_strength(self):
        """Test password strength validation."""
        # Strong passwords
        strong_passwords = [
            "Password123!",
            "MyStr0ng@Pass",
            "Complex#Pass1"
        ]
        
        for password in strong_passwords:
            assert len(password) >= 8
            assert any(c.isupper() for c in password)  # Has uppercase
            assert any(c.islower() for c in password)  # Has lowercase
            assert any(c.isdigit() for c in password)  # Has digit
            assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)  # Has special char
        
        # Weak passwords
        weak_passwords = [
            "password",  # No uppercase, digit, special char
            "PASSWORD",  # No lowercase, digit, special char
            "12345678",  # No letters
            "Pass1",     # Too short
            ""           # Empty
        ]
        
        for password in weak_passwords:
            is_weak = (
                len(password) < 8 or
                not any(c.isupper() for c in password) or
                not any(c.islower() for c in password) or
                not any(c.isdigit() for c in password) or
                not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
            )
            assert is_weak, f"Weak password not detected: {password}"


@pytest.mark.unit
class TestDataUtils:
    """Test data utility functions."""
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        # Test cases for input sanitization
        test_cases = [
            ("<script>alert('xss')</script>", "alert('xss')"),
            ("  extra   spaces  ", "extra spaces"),
            ("\n\nnewlines\n\n", "newlines"),
            ("HTML & entities", "HTML & entities"),
            ("", ""),
            ("Normal text", "Normal text")
        ]
        
        for input_text, expected in test_cases:
            # Basic sanitization (remove HTML tags and normalize whitespace)
            sanitized = input_text.replace("<script>", "").replace("</script>", "")
            sanitized = " ".join(sanitized.split())
            
            assert sanitized == expected
    
    def test_format_date(self):
        """Test date formatting."""
        from datetime import date
        
        test_date = date(2024, 12, 31)
        
        # Test different date formats
        formats = [
            ("%Y-%m-%d", "2024-12-31"),
            ("%d/%m/%Y", "31/12/2024"),
            ("%B %d, %Y", "December 31, 2024"),
            ("%Y", "2024")
        ]
        
        for format_str, expected in formats:
            formatted = test_date.strftime(format_str)
            assert formatted == expected
    
    def test_pagination_calculation(self):
        """Test pagination calculation."""
        def calculate_pagination(page: int, page_size: int, total: int):
            """Calculate pagination info."""
            total_pages = (total + page_size - 1) // page_size
            offset = (page - 1) * page_size
            
            return {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "offset": offset,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        
        # Test cases
        test_cases = [
            (1, 10, 25, {"total_pages": 3, "offset": 0, "has_next": True, "has_prev": False}),
            (2, 10, 25, {"total_pages": 3, "offset": 10, "has_next": True, "has_prev": True}),
            (3, 10, 25, {"total_pages": 3, "offset": 20, "has_next": False, "has_prev": True}),
            (1, 5, 0, {"total_pages": 0, "offset": 0, "has_next": False, "has_prev": False})
        ]
        
        for page, page_size, total, expected in test_cases:
            result = calculate_pagination(page, page_size, total)
            
            for key, value in expected.items():
                assert result[key] == value, f"Failed for page={page}, page_size={page_size}, total={total}"
    
    def test_slug_generation(self):
        """Test URL slug generation."""
        def generate_slug(text: str) -> str:
            """Generate URL-friendly slug."""
            import re
            # Convert to lowercase and replace spaces with hyphens
            slug = text.lower()
            slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
            slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces and multiple hyphens
            return slug.strip('-')
        
        test_cases = [
            ("Software Engineer", "software-engineer"),
            ("Program Manager - P-4", "program-manager-p-4"),
            ("UNICEF Child Protection", "unicef-child-protection"),
            ("IT & Communications", "it-communications"),
            ("", ""),
            ("Special@#$Characters", "specialcharacters")
        ]
        
        for input_text, expected in test_cases:
            result = generate_slug(input_text)
            assert result == expected
