import os
import sys

import pytest

# Add the parent directory to the path so we can import the database modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database.db import db_pool


@pytest.fixture(scope="session")
def db():
    """Set up the test database before running tests."""
    # could initialize a test database here if needed
    # For now, we'll just return the connection pool
    yield db_pool

    # Clean up after tests complete
    db_pool.closeall()
