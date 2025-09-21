import sqlite3
from typing import Tuple

import kernel.userdata as ud


class TestUserDataDatabase:

    def test_get_db_connection(self, clean_database: Tuple[str, str]) -> None:
        """Test database connection."""
        metadata_db, userdata_db = clean_database
        with ud.get_db_connection() as conn:
            assert isinstance(conn, sqlite3.Connection)
        # conn is automatically closed by the context manager

    def test_build_user_data_database(
        self, clean_database: Tuple[str, str]
    ) -> None:
        """Test building user data database."""
        metadata_db, userdata_db = clean_database

        # Clear any existing data
        with ud.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS userdata (username TEXT, groupname TEXT, info TEXT, homedir TEXT, shell TEXT, password TEXT)"
            )
            cur.execute("DELETE FROM userdata")

        # Build the user data database
        ud.build_user_data_database()

        # Check that users were created
        result = ud.get_user_data("root")
        assert result is not None
        assert result.username == "root"

        result = ud.get_user_data("chris")
        assert result is not None
        assert result.username == "chris"

    def test_get_user_data(self, clean_database: Tuple[str, str]) -> None:
        """Test user data retrieval."""
        metadata_db, userdata_db = clean_database

        # Clear any existing data
        with ud.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS userdata (username TEXT, groupname TEXT, info TEXT, homedir TEXT, shell TEXT, password TEXT)"
            )
            cur.execute("DELETE FROM userdata")

        # Build the user data database
        ud.build_user_data_database()

        result = ud.get_user_data("root")
        assert result is not None
        assert result.username == "root"
        assert result.groupname == "root"
        assert result.info == "Root"
        assert result.homedir == "/"
        assert result.shell == "/programs/interpreter"
        assert (
            result.password
            == "d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1"
        )  # hashed "pass"

    def test_get_all__user_data(self, clean_database: Tuple[str, str]) -> None:
        """Test all user data retrieval."""
        metadata_db, userdata_db = clean_database

        # Clear any existing data
        with ud.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS userdata (username TEXT, groupname TEXT, info TEXT, homedir TEXT, shell TEXT, password TEXT)"
            )
            cur.execute("DELETE FROM userdata")

        # Build the user data database
        ud.build_user_data_database()

        result = ud.get_all_user_data()
        assert result is not None
        assert len(result) >= 2  # root and chris
        usernames = [user.username for user in result]
        assert "root" in usernames
        assert "chris" in usernames
        assert "root" in usernames
        assert "chris" in usernames

    def test_get_group(self, clean_database: Tuple[str, str]) -> None:
        """Test group retrieval."""
        metadata_db, userdata_db = clean_database

        # Clear any existing data
        with ud.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS userdata (username TEXT, groupname TEXT, info TEXT, homedir TEXT, shell TEXT, password TEXT)"
            )
            cur.execute("DELETE FROM userdata")

        # Build the user data database
        ud.build_user_data_database()

        result = ud.get_group("root")
        assert result == "root"

        result = ud.get_group("chris")
        assert result == "chris"

    def test_get_info(self, clean_database: Tuple[str, str]) -> None:
        """Test user info retrieval."""
        metadata_db, userdata_db = clean_database

        # Clear any existing data
        with ud.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS userdata (username TEXT, groupname TEXT, info TEXT, homedir TEXT, shell TEXT, password TEXT)"
            )
            cur.execute("DELETE FROM userdata")

        # Build the user data database
        ud.build_user_data_database()

        result = ud.get_info("root")
        assert result == "Root"

        result = ud.get_info("chris")
        assert result == "Chris"

    def test_get_homedir(self, clean_database: Tuple[str, str]) -> None:
        """Test home directory retrieval."""
        metadata_db, userdata_db = clean_database

        # Clear any existing data
        with ud.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS userdata (username TEXT, groupname TEXT, info TEXT, homedir TEXT, shell TEXT, password TEXT)"
            )
            cur.execute("DELETE FROM userdata")

        # Build the user data database
        ud.build_user_data_database()

        result = ud.get_homedir("root")
        assert result == "/"

        result = ud.get_homedir("chris")
        assert result == "/"

    def test_get_shell(self, clean_database: Tuple[str, str]) -> None:
        """Test shell retrieval."""
        metadata_db, userdata_db = clean_database

        # Clear any existing data
        with ud.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS userdata (username TEXT, groupname TEXT, info TEXT, homedir TEXT, shell TEXT, password TEXT)"
            )
            cur.execute("DELETE FROM userdata")

        # Build the user data database
        ud.build_user_data_database()

        result = ud.get_shell("root")
        assert result == "/programs/interpreter"

        result = ud.get_shell("chris")
        assert result == "/programs/interpreter"

    def test_get_password(self, clean_database: Tuple[str, str]) -> None:
        """Test password retrieval."""
        metadata_db, userdata_db = clean_database

        # Clear any existing data
        with ud.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS userdata (username TEXT, groupname TEXT, info TEXT, homedir TEXT, shell TEXT, password TEXT)"
            )
            cur.execute("DELETE FROM userdata")

        # Build the user data database
        ud.build_user_data_database()

        result = ud.get_password("root")
        assert (
            result
            == "d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1"
        )  # hashed "pass"

        result = ud.get_password("chris")
        assert (
            result
            == "2744ccd10c7533bd736ad890f9dd5cab2adb27b07d500b9493f29cdc420cb2e0"
        )  # hashed "me"

    def test_correct_password(self, clean_database: Tuple[str, str]) -> None:
        """Test password validation."""
        metadata_db, userdata_db = clean_database

        # Clear any existing data
        with ud.get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS userdata (username TEXT, groupname TEXT, info TEXT, homedir TEXT, shell TEXT, password TEXT)"
            )
            cur.execute("DELETE FROM userdata")

        # Build the user data database
        ud.build_user_data_database()

        # Test correct password
        result = ud.correct_password(
            "root",
            "d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1",
        )
        assert result is True

        # Test incorrect password
        result = ud.correct_password("root", "wrongpassword")
        assert result is False

        # Test non-existent user
        result = ud.correct_password("nonexistent", "anypassword")
        assert result is False

        # Test incorrect password
        result = ud.correct_password("root", "wrongpassword")
        assert result is False

        # Test non-existent user
        result = ud.correct_password("nonexistent", "anypassword")
        assert result is False
