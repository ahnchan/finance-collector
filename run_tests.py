#!/usr/bin/env python3
"""
Script to run tests for the Finance Collector API

$ python run_tests.py

"""
import os
import sys
import pytest


def main():
    """Run the tests"""
    # Add the current directory to the Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Run the tests
    args = [
        "-v",  # Verbose output
        "--cov=app",  # Measure code coverage for the app package
        "--cov=main",  # Measure code coverage for the main module
        "--cov-report=term",  # Output coverage report to terminal
        "--cov-report=html:coverage_html",  # Output HTML coverage report
        "tests/",  # Directory containing tests
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run pytest with the arguments
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(main())
