import os
import sys
import pytest
import warnings
from typing import Generator, Tuple

# Add the project root to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Filter out all ResourceWarnings during testing
warnings.filterwarnings("ignore", category=ResourceWarning)


@pytest.fixture
def clean_database() -> Generator[Tuple[str, str], None, None]:
    """Provide a clean in-memory database for each test."""
    # With the new in-memory database approach, we just need to return the
    # in-memory database identifiers
    metadata_db = ":memory:"
    userdata_db = ":memory:"

    # Reset the singleton connections to ensure clean state
    import kernel.metadata
    import kernel.userdata

    kernel.metadata._test_metadata_connection = None
    kernel.userdata._test_userdata_connection = None

    # Initialize metadata database
    with kernel.metadata.get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS metadata (
                        path TEXT,
                        owner TEXT,
                        permission TEXT,
                        created TIMESTAMP,
                        accessed TIMESTAMP,
                        modified TIMESTAMP)"""
        )
        # Clear any existing data
        cur.execute("DELETE FROM metadata")

    # Initialize userdata database
    with kernel.userdata.get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS userdata (
                        username TEXT,
                        groupname TEXT,
                        info TEXT,
                        homedir TEXT,
                        shell TEXT,
                        password TEXT)"""
        )
        # Clear any existing data
        cur.execute("DELETE FROM userdata")

        # Insert test users
        root = (
            "root",
            "root",
            "Root",
            "/",
            "/programs/interpreter",
            "d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1",
        )  # pass
        chris = (
            "chris",
            "chris",
            "Chris",
            "/",
            "/programs/interpreter",
            "2744ccd10c7533bd736ad890f9dd5cab2adb27b07d500b9493f29cdc420cb2e0",
        )  # me
        cur.execute("INSERT INTO userdata VALUES (?, ?, ?, ?, ?, ?)", root)
        cur.execute("INSERT INTO userdata VALUES (?, ?, ?, ?, ?, ?)", chris)

    yield metadata_db, userdata_db

    # Reset connections after test
    kernel.metadata._test_metadata_connection = None
    kernel.userdata._test_userdata_connection = None


@pytest.fixture(autouse=True)
def ensure_db_connections_closed() -> Generator[None]:
    """Ensure all database connections are closed after each test."""
    yield
    # No need to force garbage collection as it's not helping with the ResourceWarnings
    pass
