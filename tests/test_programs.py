import pytest
from unittest.mock import patch, MagicMock

import programs.ls as ls_program
import programs.cat as cat_program
from typing import Any


class TestLsProgram:

    @pytest.fixture
    def mock_shell(self) -> Any:
        """Create a mock shell."""
        return MagicMock()

    def test_ls_help(self) -> None:
        """Test ls help message."""
        help_text = ls_program.help()
        assert isinstance(help_text, str)
        assert len(help_text) > 0

    @pytest.mark.database
    def test_ls_run_no_args(self, mock_shell: Any) -> None:
        """Test ls run with no arguments."""
        mock_shell.get_path.return_value = "/"
        mock_shell.syscall.list_dir.return_value = ["file1.txt", "file2.txt"]
        mock_shell.syscall.get_meta_data.return_value = (
            "file1.txt",
            "root",
            "rw-r--r--",
            "created",
            "accessed",
            "modified",
        )
        mock_shell.syscall.exists.return_value = True

        ls_program.run(mock_shell, [])

        # Check that list_dir was called
        mock_shell.syscall.list_dir.assert_called_once()

    @pytest.mark.database
    def test_ls_run_with_paths(self, mock_shell: Any) -> None:
        """Test ls run with specific paths."""
        mock_shell.syscall.list_dir.return_value = ["file1.txt", "file2.txt"]
        mock_shell.syscall.get_meta_data.return_value = (
            "file1.txt",
            "root",
            "rw-r--r--",
            "created",
            "accessed",
            "modified",
        )
        mock_shell.syscall.exists.return_value = True

        # Mock the resolve_path function
        with patch(
            "programs.ls.resolve_path",
            side_effect=lambda shell, path: f"/test/{path}",
        ):
            ls_program.run(mock_shell, ["dir1", "dir2"])

            # Check that list_dir was called for each path
            assert mock_shell.syscall.list_dir.call_count == 2

    def test_ls_run_long_format(self, mock_shell: Any) -> None:
        """Test ls run with long format."""
        mock_shell.syscall.list_dir.return_value = ["file1.txt"]
        mock_shell.syscall.get_meta_data.return_value = (
            "/test/file1.txt",
            "root",
            "rw-r--r--",
            "created",
            "accessed",
            "modified",
        )
        mock_shell.syscall.base_name.return_value = "file1.txt"
        mock_shell.syscall.exists.return_value = True

        with patch(
            "programs.ls.resolve_path",
            side_effect=lambda shell, path: f"/test/{path}",
        ):
            ls_program.run(mock_shell, ["-l", "test_dir"])

            # Check that stdout was written with long format
            mock_shell.stdout.write.assert_called_once()

    @pytest.mark.database
    def test_ls_run_nonexistent_path(self, mock_shell: Any) -> None:
        """Test ls run with nonexistent path."""
        mock_shell.syscall.exists.return_value = False

        with patch(
            "programs.ls.resolve_path",
            side_effect=lambda shell, path: f"/nonexistent/{path}",
        ):
            ls_program.run(mock_shell, ["nonexistent"])

            # Check that stderr was written with error message
            mock_shell.stderr.write.assert_called_once()


class TestCatProgram:

    @pytest.fixture
    def mock_shell(self) -> Any:
        """Create a mock shell."""
        return MagicMock()

    def test_cat_help(self) -> None:
        """Test cat help message."""
        help_text = cat_program.help()
        assert isinstance(help_text, str)
        assert "Concatenate" in help_text

    def test_cat_run_no_args_no_stdin(self, mock_shell: Any) -> None:
        """Test cat run with no args and no stdin."""
        mock_shell.stdin = None
        cat_program.run(mock_shell, [])

        # Check that stderr was written with error message
        mock_shell.stderr.write.assert_called_once_with("missing file operand")

    def test_cat_run_with_files(self, mock_shell: Any) -> None:
        """Test cat run with files."""
        # Mock file content
        mock_file = MagicMock()
        mock_file.__iter__ = MagicMock(
            return_value=iter(["line1\n", "line2\n"])
        )
        mock_file.readline = MagicMock(return_value="line1\n")

        mock_shell.stdin = None
        mock_shell.syscall.open_file = MagicMock(return_value=mock_file)
        mock_shell.syscall.exists = MagicMock(return_value=True)

        with patch(
            "programs.cat.resolve_path",
            side_effect=lambda shell, path: f"/test/{path}",
        ):
            cat_program.run(mock_shell, ["file1.txt", "file2.txt"])

            # Check that files were opened
            assert mock_shell.syscall.open_file.call_count == 2
            # Check that stdout was written
            assert (
                mock_shell.stdout.write.call_count >= 2
            )  # At least 2 lines written

    def test_cat_run_with_stdin(self, mock_shell: Any) -> None:
        """Test cat run with stdin."""
        mock_shell.stdin = MagicMock()
        mock_shell.stdin.read.return_value = ["line1\n", "line2\n"]

        cat_program.run(mock_shell, [])

        # Check that stdin was read
        mock_shell.stdin.read.assert_called_once()
        # Check that stdout was written
        assert mock_shell.stdout.write.call_count == 2
