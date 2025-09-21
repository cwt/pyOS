import os
import tempfile
import pytest
from unittest.mock import patch

import kernel.filesystem as fs
from kernel.constants import BASEPATH
from typing import Generator


def test_abs_path() -> None:
    """Test absolute path conversion."""
    test_path = "/test/path"
    expected = os.path.abspath(os.path.join(BASEPATH, test_path.lstrip("/")))
    assert fs.abs_path(test_path) == expected


def test_rel_path() -> None:
    """Test relative path conversion."""
    path = "/test/path/file.txt"
    base = "/test"
    expected = os.path.relpath(path, base)
    assert fs.rel_path(path, base) == expected


def test_irel_path() -> None:
    """Test internal relative path conversion."""
    # Mock the BASEPATH for consistent testing
    with patch("kernel.filesystem.BASEPATH", "/mocked/base"):
        test_path = "/mocked/base/test/file.txt"
        expected = "test/file.txt"
        assert fs.irel_path(test_path) == expected


def test_iabs_path() -> None:
    """Test internal absolute path conversion."""
    with patch("kernel.filesystem.BASEPATH", "/home/cwt/Projects/pyOS"):
        test_path = "/home/cwt/Projects/pyOS/test/file.txt"
        expected = "/test/file.txt"
        assert fs.iabs_path(test_path) == expected


def test_join_path() -> None:
    """Test path joining."""
    paths = ["/test", "path", "file.txt"]
    expected = os.path.join(*paths)
    assert fs.join_path(*paths) == expected


def test_dir_name() -> None:
    """Test directory name extraction."""
    path = "/test/path/file.txt"
    expected = os.path.dirname(path)
    assert fs.dir_name(path) == expected


def test_base_name() -> None:
    """Test base name extraction."""
    path = "/test/path/file.txt"
    expected = os.path.basename(path)
    assert fs.base_name(path) == expected


def test_split() -> None:
    """Test path splitting."""
    path = "/test/path/file.txt"
    expected = (os.path.dirname(path), os.path.basename(path))
    assert fs.split(path) == expected


# Tests that require filesystem operations
class TestFilesystemOperations:

    @pytest.fixture(autouse=True)
    def setup_temp_dir(self) -> Generator[None, None, None]:
        """Set up a temporary directory for filesystem tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        self.test_dir = os.path.join(self.temp_dir, "test_dir")

        # Create test file
        with open(self.test_file, "w") as f:
            f.write("test content")

        yield

        # Cleanup
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    def test_exists(self) -> None:
        """Test exists method."""
        with patch("kernel.filesystem.BASEPATH", self.temp_dir):
            assert fs.exists("test.txt") is True
            assert fs.exists("nonexistent.txt") is False

    def test_is_file(self) -> None:
        """Test is_file method."""
        with patch("kernel.filesystem.BASEPATH", self.temp_dir):
            assert fs.is_file("test.txt") is True
            assert fs.is_file("nonexistent.txt") is False

    def test_is_dir(self) -> None:
        """Test is_dir method."""
        os.mkdir(self.test_dir)
        with patch("kernel.filesystem.BASEPATH", self.temp_dir):
            assert fs.is_dir("test_dir") is True
            assert fs.is_dir("test.txt") is False

    def test_get_size(self) -> None:
        """Test get_size method."""
        with patch("kernel.filesystem.BASEPATH", self.temp_dir):
            size = fs.get_size("test.txt")
            assert size == len("test content")

    def test_list_dir(self) -> None:
        """Test list_dir method."""
        os.mkdir(self.test_dir)
        with patch("kernel.filesystem.BASEPATH", self.temp_dir):
            listing = fs.list_dir("/")
            assert "test.txt" in listing
            assert "test_dir" in listing

    def test_make_dir(self) -> None:
        """Test make_dir method."""
        new_dir = os.path.join(self.temp_dir, "new_dir")
        with patch("kernel.filesystem.BASEPATH", self.temp_dir):
            fs.make_dir("new_dir")
            assert os.path.exists(new_dir) is True
            assert os.path.isdir(new_dir) is True

    def test_open_file(self) -> None:
        """Test open_file method."""
        with patch("kernel.filesystem.BASEPATH", self.temp_dir):
            f = fs.open_file("test.txt", "r")
            content = f.read()
            f.close()
            assert content == "test content"

    def test_remove(self) -> None:
        """Test remove method."""
        with patch("kernel.filesystem.BASEPATH", self.temp_dir):
            assert os.path.exists(self.test_file) is True
            fs.remove("test.txt")
            assert os.path.exists(self.test_file) is False
