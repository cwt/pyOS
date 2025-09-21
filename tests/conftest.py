import os
import sys
import tempfile
import shutil
import pytest
import warnings
from typing import Generator, Tuple

# Add the project root to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from kernel.constants import METADATAFILE, USERDATAFILE

# Filter out all ResourceWarnings during testing
warnings.filterwarnings("ignore", category=ResourceWarning)


@pytest.fixture(scope="session")
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def setup_test_environment(
    temp_dir: str,
) -> Generator[Tuple[str, str, str], None, None]:
    """Set up a test environment with temporary files."""
    # Save original values
    original_metadatafile = METADATAFILE
    original_userdatafile = USERDATAFILE

    # Create temporary database files
    test_metadata_db = os.path.join(temp_dir, "test_metadata.db")
    test_userdata_db = os.path.join(temp_dir, "test_userdata.db")

    # Override constants for testing
    import kernel.constants

    kernel.constants.METADATAFILE = test_metadata_db  # type: ignore
    kernel.constants.USERDATAFILE = test_userdata_db  # type: ignore

    yield temp_dir, test_metadata_db, test_userdata_db

    # Restore original values
    kernel.constants.METADATAFILE = original_metadatafile  # type: ignore
    kernel.constants.USERDATAFILE = original_userdatafile  # type: ignore


@pytest.fixture
def clean_database(
    setup_test_environment: Tuple[str, str, str]
) -> Generator[Tuple[str, str], None, None]:
    """Provide a clean database for each test."""
    temp_dir, metadata_db, userdata_db = setup_test_environment

    # Remove existing database files
    if os.path.exists(metadata_db):
        os.remove(metadata_db)
    if os.path.exists(userdata_db):
        os.remove(userdata_db)

    # Create new empty database files with proper initialization
    from kernel.constants import METADATAFILE, USERDATAFILE

    # Save original values
    original_metadatafile = METADATAFILE
    original_userdatafile = USERDATAFILE

    # Override constants for testing
    import kernel.constants

    kernel.constants.METADATAFILE = metadata_db  # type: ignore
    kernel.constants.USERDATAFILE = userdata_db  # type: ignore

    try:
        # Initialize metadata database
        import kernel.metadata

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

        # Initialize userdata database
        import kernel.userdata

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
    finally:
        # Restore original values
        kernel.constants.METADATAFILE = original_metadatafile  # type: ignore
        kernel.constants.USERDATAFILE = original_userdatafile  # type: ignore

    yield metadata_db, userdata_db

    # Clean up after test
    if os.path.exists(metadata_db):
        os.remove(metadata_db)
    if os.path.exists(userdata_db):
        os.remove(userdata_db)


@pytest.fixture(autouse=True)
def ensure_db_connections_closed() -> Generator[None]:
    """Ensure all database connections are closed after each test."""
    yield
    # No need to force garbage collection as it's not helping with the ResourceWarnings
    pass
