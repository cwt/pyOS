import pytest
import datetime
import sqlite3
from unittest.mock import patch
from typing import Any, Generator
from typing import Tuple

import kernel.metadata as md


class TestMetadataDatabase:

    def test_get_db_connection(self, clean_database: Any) -> None:
        """Test database connection context manager."""
        metadata_db, userdata_db = clean_database
        with md.get_db_connection() as conn:
            assert isinstance(conn, sqlite3.Connection)
        # conn is automatically closed by the context manager

    def test_execute_query(self, clean_database: Any) -> None:
        """Test query execution."""
        metadata_db, userdata_db = clean_database

        # Create table
        with md.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS test_table_query (id INTEGER, name TEXT)"
            )
            cur.execute(
                "DELETE FROM test_table_query"
            )  # Clear any existing data

        # Test insert query with no fetch
        result = md.execute_query(
            "INSERT INTO test_table_query VALUES (1, 'test')", fetch="none"
        )
        assert result is None

        # Test fetch all
        result = md.execute_query("SELECT * FROM test_table_query", fetch="all")
        assert result == [(1, "test")]

        # Test fetch one
        result = md.execute_query("SELECT * FROM test_table_query", fetch="one")
        assert result == (1, "test")

    def test_execute_many(self, clean_database: Any) -> None:
        """Test multiple query execution."""
        metadata_db, userdata_db = clean_database

        # Create table
        with md.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS test_table_many (id INTEGER, name TEXT)"
            )
            # Clear any existing data
            cur.execute("DELETE FROM test_table_many")

        # Test executemany
        queries = [(1, "test1"), (2, "test2"), (3, "test3")]
        result = md.execute_many(
            "INSERT INTO test_table_many VALUES (?, ?)", queries
        )
        assert result is True

        # Verify insertion
        result = md.execute_query("SELECT * FROM test_table_many", fetch="all")
        assert result is not None
        assert len(result) == 3  # type: ignore


class TestMetadataFunctions:

    @pytest.fixture
    def setup_metadata_table(
        self, clean_database: Any
    ) -> Generator[Tuple[Any, Any], None, None]:
        """Set up metadata table with test data."""
        metadata_db, userdata_db = clean_database

        # Create metadata table
        with md.get_db_connection() as conn:
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
            now = datetime.datetime.now()
            cur.execute(
                "INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)",
                ("/test/file.txt", "root", "rwxrwxrwx", now, now, now),
            )

        yield metadata_db, userdata_db

        # Clean up is handled by clean_database fixture

    def test_get_meta_data(self, setup_metadata_table: Any) -> None:
        """Test metadata retrieval."""
        metadata_db, userdata_db = setup_metadata_table

        result = md.get_meta_data("/test/file.txt")
        assert result is not None
        assert result.path == "/test/file.txt"
        assert result.owner == "root"
        assert result.permission == "rwxrwxrwx"

    def test_get_all_meta_data(self, setup_metadata_table: Any) -> None:
        """Test all metadata retrieval."""
        metadata_db, userdata_db = setup_metadata_table

        # Add another entry
        with md.get_db_connection() as conn:
            cur = conn.cursor()
            now = datetime.datetime.now()
            cur.execute(
                "INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)",
                ("/test/another.txt", "user", "rw-r--r--", now, now, now),
            )

        result = md.get_all_meta_data()
        assert result is not None
        assert len(result) == 2
        paths = [item.path for item in result]
        assert "/test/file.txt" in paths
        assert "/test/another.txt" in paths

    def test_add_path(self, clean_database: Any) -> None:
        """Test adding path metadata."""
        metadata_db, userdata_db = clean_database

        # Create metadata table
        with md.get_db_connection() as conn:
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

        now = datetime.datetime.now()
        with patch("kernel.metadata.datetime") as mock_datetime:
            mock_datetime.datetime.now.return_value = now
            md.add_path("/new/file.txt", "root", "rwxrwxrwx")

        result = md.get_meta_data("/new/file.txt")
        assert result is not None
        assert result.path == "/new/file.txt"
        assert result.owner == "root"
        assert result.permission == "rwxrwxrwx"

    def test_delete_path(self, setup_metadata_table: Any) -> None:
        """Test deleting path metadata."""
        metadata_db, userdata_db = setup_metadata_table

        md.delete_path("/test/file.txt")
        result = md.get_meta_data("/test/file.txt")
        assert result is None

    def test_get_permission_string(self, setup_metadata_table: Any) -> None:
        """Test permission string retrieval."""
        metadata_db, userdata_db = setup_metadata_table

        result = md.get_permission_string("/test/file.txt")
        assert result == "rwxrwxrwx"

    def test_get_permission_number(self, setup_metadata_table: Any) -> None:
        """Test permission number calculation."""
        metadata_db, userdata_db = setup_metadata_table

        result = md.get_permission_number("/test/file.txt")
        # rwxrwxrwx should convert to 777
        assert result == "777"

    def test_set_permission_string(self, setup_metadata_table: Any) -> None:
        """Test setting permission string."""
        metadata_db, userdata_db = setup_metadata_table

        # The set_permission_string function converts the string to a number first
        # Let's test with a valid permission string
        md.set_permission_string("/test/file.txt", "rw-r--r--")
        result = md.get_permission_string("/test/file.txt")
        # The result should be the same permission string
        assert result == "rw-r--r--"

    def test_set_permission_number(self, setup_metadata_table: Any) -> None:
        """Test setting permission number."""
        metadata_db, userdata_db = setup_metadata_table

        # Test with number (as string to match validation)
        md.set_permission_number("/test/file.txt", "644")
        result = md.get_permission_number("/test/file.txt")
        assert result == "644"

    def test_set_permission(self, setup_metadata_table: Any) -> None:
        """Test setting permission with either string or number."""
        metadata_db, userdata_db = setup_metadata_table

        # Test with string
        md.set_permission("/test/file.txt", "rw-r--r--")
        result = md.get_permission_string("/test/file.txt")
        assert result == "rw-r--r--"

        # Test with number (as integer)
        md.set_permission("/test/file.txt", 644)
        result = md.get_permission_number("/test/file.txt")
        assert result == "644"

    def test_get_time(self, setup_metadata_table: Any) -> None:
        """Test time retrieval."""
        metadata_db, userdata_db = setup_metadata_table

        result = md.get_time("/test/file.txt")
        assert len(result) == 3  # created, accessed, modified
        assert all(isinstance(t, datetime.datetime) for t in result)

    def test_get_owner(self, setup_metadata_table: Any) -> None:
        """Test owner retrieval."""
        metadata_db, userdata_db = setup_metadata_table

        result = md.get_owner("/test/file.txt")
        assert result == "root"

    def test_set_owner(self, setup_metadata_table: Any) -> None:
        """Test setting owner."""
        metadata_db, userdata_db = setup_metadata_table

        md.set_owner("/test/file.txt", "newuser")
        result = md.get_owner("/test/file.txt")
        assert result == "newuser"

    def test_validate_permission(self) -> None:
        """Test permission validation."""
        # Valid permissions
        md.validate_permission("rwxrwxrwx")
        md.validate_permission("rw-r--r--")
        md.validate_permission("---------")

        # Invalid permissions should raise AssertionError
        with pytest.raises(AssertionError):
            md.validate_permission("invalid")

        with pytest.raises(AssertionError):
            md.validate_permission("rwxrwxrwxextra")
