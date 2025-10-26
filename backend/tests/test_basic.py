"""Simple test to verify testing setup."""
import pytest


def test_basic_functionality():
    """Test basic Python functionality."""
    assert 1 + 1 == 2
    assert "hello" == "hello"
    assert True is True


def test_string_operations():
    """Test string operations."""
    text = "UN Jobs Hub"
    assert len(text) == 11
    assert "Jobs" in text
    assert text.lower() == "un jobs hub"


def test_list_operations():
    """Test list operations."""
    items = ["Python", "JavaScript", "React", "FastAPI"]
    assert len(items) == 4
    assert "Python" in items
    assert "Vue" not in items


@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (0, 0),
])
def test_double_function(input_value, expected):
    """Test parametrized test."""
    assert input_value * 2 == expected


class TestMathOperations:
    """Test class for math operations."""
    
    def test_addition(self):
        """Test addition."""
        assert 5 + 3 == 8
    
    def test_subtraction(self):
        """Test subtraction."""
        assert 10 - 4 == 6
    
    def test_multiplication(self):
        """Test multiplication."""
        assert 3 * 4 == 12
    
    def test_division(self):
        """Test division."""
        assert 15 / 3 == 5
