#!/usr/bin/env python3
"""
Test runner for Git Merge Conflict Resolver Backend
"""
import subprocess
import sys
import os

def run_tests():
    """Run all tests"""
    print("🧪 Running tests...")
    
    # Run pytest with coverage
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "app/tests/", 
        "-v", 
        "--tb=short",
        "--cov=app/src",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov"
    ])
    
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return result.returncode

def run_linting():
    """Run code linting"""
    print("🔍 Running code linting...")
    
    # Run black
    print("  - Running Black (code formatting)...")
    subprocess.run([sys.executable, "-m", "black", "app/src/", "app/tests/", "--check"])
    
    # Run isort
    print("  - Running isort (import sorting)...")
    subprocess.run([sys.executable, "-m", "isort", "app/src/", "app/tests/", "--check-only"])
    
    # Run flake8
    print("  - Running flake8 (code quality)...")
    subprocess.run([sys.executable, "-m", "flake8", "app/src/", "app/tests/"])

if __name__ == "__main__":
    print("🚀 Git Merge Conflict Resolver - Test Suite")
    print("=" * 50)
    
    # Run linting
    run_linting()
    
    # Run tests
    exit_code = run_tests()
    
    print("=" * 50)
    if exit_code == 0:
        print("🎉 All checks passed!")
    else:
        print("💥 Some checks failed!")
    
    sys.exit(exit_code) 