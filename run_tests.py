#!/usr/bin/env python3
"""Test runner script for UN Jobs Hub."""
import asyncio
import sys
import subprocess
import os
from pathlib import Path


def run_command(command: str, cwd: str = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"


def install_test_dependencies():
    """Install test dependencies."""
    print("📦 Installing test dependencies...")
    
    backend_dir = Path(__file__).parent / "backend"
    requirements_file = backend_dir / "requirements-test.txt"
    
    if requirements_file.exists():
        exit_code, stdout, stderr = run_command(
            f"pip install -r {requirements_file}",
            cwd=backend_dir
        )
        
        if exit_code != 0:
            print(f"❌ Failed to install test dependencies: {stderr}")
            return False
        else:
            print("✅ Test dependencies installed successfully")
            return True
    else:
        print("⚠️  Test requirements file not found, skipping dependency installation")
        return True


def run_backend_tests():
    """Run backend tests."""
    print("\n🧪 Running backend tests...")
    
    backend_dir = Path(__file__).parent / "backend"
    
    # Run pytest with coverage
    exit_code, stdout, stderr = run_command(
        "pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing",
        cwd=backend_dir
    )
    
    print(stdout)
    if stderr:
        print(f"Errors: {stderr}")
    
    if exit_code == 0:
        print("✅ Backend tests passed!")
        return True
    else:
        print("❌ Backend tests failed!")
        return False


def run_frontend_tests():
    """Run frontend tests."""
    print("\n🧪 Running frontend tests...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check if package.json exists
    if not (frontend_dir / "package.json").exists():
        print("⚠️  Frontend package.json not found, skipping frontend tests")
        return True
    
    # Install dependencies if needed
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        exit_code, stdout, stderr = run_command("npm install", cwd=frontend_dir)
        if exit_code != 0:
            print(f"❌ Failed to install frontend dependencies: {stderr}")
            return False
    
    # Run tests
    exit_code, stdout, stderr = run_command("npm test", cwd=frontend_dir)
    
    print(stdout)
    if stderr:
        print(f"Errors: {stderr}")
    
    if exit_code == 0:
        print("✅ Frontend tests passed!")
        return True
    else:
        print("❌ Frontend tests failed!")
        return False


def run_linting():
    """Run code linting."""
    print("\n🔍 Running code linting...")
    
    backend_dir = Path(__file__).parent / "backend"
    frontend_dir = Path(__file__).parent / "frontend"
    
    all_passed = True
    
    # Backend linting
    print("Backend linting...")
    exit_code, stdout, stderr = run_command("python -m flake8 . --max-line-length=100", cwd=backend_dir)
    if exit_code != 0:
        print(f"❌ Backend linting failed: {stderr}")
        all_passed = False
    else:
        print("✅ Backend linting passed")
    
    # Frontend linting
    if (frontend_dir / "package.json").exists():
        print("Frontend linting...")
        exit_code, stdout, stderr = run_command("npm run lint", cwd=frontend_dir)
        if exit_code != 0:
            print(f"❌ Frontend linting failed: {stderr}")
            all_passed = False
        else:
            print("✅ Frontend linting passed")
    
    return all_passed


def run_type_checking():
    """Run type checking."""
    print("\n🔍 Running type checking...")
    
    backend_dir = Path(__file__).parent / "backend"
    frontend_dir = Path(__file__).parent / "frontend"
    
    all_passed = True
    
    # Backend type checking
    print("Backend type checking...")
    exit_code, stdout, stderr = run_command("python -m mypy . --ignore-missing-imports", cwd=backend_dir)
    if exit_code != 0:
        print(f"❌ Backend type checking failed: {stderr}")
        all_passed = False
    else:
        print("✅ Backend type checking passed")
    
    # Frontend type checking
    if (frontend_dir / "package.json").exists():
        print("Frontend type checking...")
        exit_code, stdout, stderr = run_command("npm run type-check", cwd=frontend_dir)
        if exit_code != 0:
            print(f"❌ Frontend type checking failed: {stderr}")
            all_passed = False
        else:
            print("✅ Frontend type checking passed")
    
    return all_passed


def generate_test_report():
    """Generate test report."""
    print("\n📊 Generating test report...")
    
    backend_dir = Path(__file__).parent / "backend"
    
    # Check if coverage report exists
    coverage_html = backend_dir / "htmlcov" / "index.html"
    if coverage_html.exists():
        print(f"📈 Coverage report generated: {coverage_html}")
        print("Open the HTML file in your browser to view detailed coverage")
    else:
        print("⚠️  Coverage report not found")


def main():
    """Main test runner."""
    print("🚀 UN Jobs Hub Test Suite")
    print("=" * 50)
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    run_backend = "--backend" in args or "--all" in args or len(args) == 0
    run_frontend = "--frontend" in args or "--all" in args or len(args) == 0
    run_lint = "--lint" in args or "--all" in args or len(args) == 0
    run_type_check = "--type-check" in args or "--all" in args or len(args) == 0
    install_deps = "--install-deps" in args
    
    success = True
    
    # Install dependencies if requested
    if install_deps:
        if not install_test_dependencies():
            success = False
    
    # Run tests
    if run_backend:
        if not run_backend_tests():
            success = False
    
    if run_frontend:
        if not run_frontend_tests():
            success = False
    
    # Run linting
    if run_lint:
        if not run_linting():
            success = False
    
    # Run type checking
    if run_type_check:
        if not run_type_checking():
            success = False
    
    # Generate report
    generate_test_report()
    
    # Final result
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
