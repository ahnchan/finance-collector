import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set test environment variables if not already set
if not os.getenv("CLIENT_ID"):
    os.environ["CLIENT_ID"] = "sample_client_id"
if not os.getenv("CLIENT_SECRET"):
    os.environ["CLIENT_SECRET"] = "sample_client_secret"
if not os.getenv("JWT_SECRET_KEY"):
    os.environ["JWT_SECRET_KEY"] = "test_secret_key"
if not os.getenv("JWT_ALGORITHM"):
    os.environ["JWT_ALGORITHM"] = "HS256"
if not os.getenv("JWT_EXPIRATION_MINUTES"):
    os.environ["JWT_EXPIRATION_MINUTES"] = "30"


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment"""
    # This fixture runs automatically before any tests
    # We can use it to set up any global test configuration
    
    # Yield to allow tests to run
    yield
    
    # Clean up after tests if needed
    pass
