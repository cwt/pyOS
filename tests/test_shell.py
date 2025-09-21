import pytest
from unittest.mock import patch, MagicMock

import kernel.shell as shell
from kernel.constants import PROGRAMSDIR
from typing import Any


class TestShell:

    @pytest.fixture
    def mock_shell(self) -> Any:
        """Create a mock shell instance."""
        with patch("kernel.system.SysCall"):
            mock_shell = shell.Shell(0, path="/test")
            return mock_shell

    def test_shell_initialization(self) -> None:
        """Test shell initialization."""
        with patch("kernel.system.SysCall"):
            mock_shell = shell.Shell(0, path="/test")

            assert mock_shell.pid == 0
            assert mock_shell.path == "/test"
            assert hasattr(mock_shell, "syscall")
            assert hasattr(mock_shell, "stdin")
            assert hasattr(mock_shell, "stdout")
            assert hasattr(mock_shell, "stderr")
            assert isinstance(mock_shell.vars, dict)
            assert isinstance(mock_shell.aliases, dict)
            assert isinstance(mock_shell.prevcommands, list)

    def test_shell_initialization_with_parent(self) -> None:
        """Test shell initialization with parent shell."""
        with patch("kernel.system.SysCall"):
            parent_shell = shell.Shell(0, path="/parent")
            parent_shell.vars = {"TEST_VAR": "test_value"}
            parent_shell.aliases = {"test_alias": "test_command"}
            parent_shell.prevcommands = ["command1", "command2"]

            mock_shell = shell.Shell(1, parent=parent_shell, path="/child")

            assert mock_shell.vars["TEST_VAR"] == "test_value"
            assert mock_shell.aliases["test_alias"] == "test_command"
            assert mock_shell.prevcommands == ["command1", "command2"]

    def test_get_path(self, mock_shell: Any) -> None:
        """Test get_path method."""
        assert mock_shell.path == "/test"

    def test_set_path(self, mock_shell: Any) -> None:
        """Test set_path method."""
        with patch.object(mock_shell, "sabs_path", side_effect=lambda x: x):
            mock_shell.path = "/new/path"
            assert mock_shell.path == "/new/path"
            assert mock_shell.old_path == "/test"  # Previous path

    def test_sabs_path_absolute(self, mock_shell: Any) -> None:
        """Test sabs_path with absolute path."""
        mock_syscall = MagicMock()
        mock_syscall.iabs_path.return_value = "/absolute/path"
        mock_shell.syscall = mock_syscall

        result = mock_shell.sabs_path("/absolute/path")
        assert result == "/absolute/path"
        mock_shell.syscall.iabs_path.assert_called_once_with("/absolute/path")

    def test_sabs_path_relative(self, mock_shell: Any) -> None:
        """Test sabs_path with relative path."""
        mock_syscall = MagicMock()
        mock_syscall.join_path.return_value = "/test/relative"
        mock_syscall.iabs_path.return_value = "/test/relative"
        mock_shell.syscall = mock_syscall

        result = mock_shell.sabs_path("relative")
        mock_shell.syscall.join_path.assert_called_once_with(
            "/test", "relative"
        )
        mock_shell.syscall.iabs_path.assert_called_once_with("/test/relative")
        assert result == "/test/relative"

    def test_srel_path(self, mock_shell: Any) -> None:
        """Test srel_path method."""
        mock_syscall = MagicMock()
        mock_syscall.rel_path.return_value = "relative/path"
        mock_shell.syscall = mock_syscall

        result = mock_shell.srel_path("/absolute/path", "/base")
        mock_shell.syscall.rel_path.assert_called_once()
        assert result == "relative/path"

    def test_program_paths_with_local(self, mock_shell: Any) -> None:
        """Test program_paths with local path (./)."""
        # For local paths, we expect the path to be resolved correctly
        with patch.object(
            mock_shell, "sabs_path", side_effect=lambda x: "/test/test"
        ):
            result = mock_shell.program_paths("./test")
            assert result == ["/test/test"]

    def test_program_paths_with_global(self, mock_shell: Any) -> None:
        """Test program_paths with global path."""
        mock_syscall = MagicMock()
        mock_syscall.join_path.side_effect = lambda x, y: f"{x}/{y}"
        mock_shell.syscall = mock_syscall

        with patch.object(
            mock_shell, "get_var", return_value=f"{PROGRAMSDIR}:/other/path"
        ):
            result = mock_shell.program_paths("test")
            expected = [f"{PROGRAMSDIR}/test", "/other/path/test"]
            assert result == expected

    def test_get_var(self, mock_shell: Any) -> None:
        """Test get_var method."""
        mock_shell.vars = {"TEST_VAR": "test_value"}

        # Test with string
        result = mock_shell.get_var("TEST_VAR")
        assert result == "test_value"

        # Test with non-existent variable
        result = mock_shell.get_var("NON_EXISTENT")
        assert result == ""

    def test_set_var(self, mock_shell: Any) -> None:
        """Test set_var method."""
        mock_shell.set_var("NEW_VAR", "new_value")
        assert mock_shell.vars["NEW_VAR"] == "new_value"

    def test_hist_find_start(self, mock_shell: Any) -> None:
        """Test hist_find with start matching."""
        mock_shell.prevcommands = ["ls -l", "cat file.txt", "ls -a"]
        result = mock_shell.hist_find("ls")
        assert result == "ls -a"  # Most recent match

    def test_hist_find_contains(self, mock_shell: Any) -> None:
        """Test hist_find with contains matching."""
        mock_shell.prevcommands = ["ls -l", "cat file.txt", "ls -a"]
        result = mock_shell.hist_find("file", start=False)
        assert result == "cat file.txt"

    def test_find_program(self, mock_shell: Any) -> None:
        """Test find_program method."""
        mock_syscall = MagicMock()
        mock_syscall.open_program.return_value = "program_module"
        mock_shell.syscall = mock_syscall

        with patch.object(
            mock_shell, "program_paths", return_value=["/programs/test.py"]
        ):
            result = mock_shell.find_program("test")
            assert result == "program_module"
            mock_shell.program_paths.assert_called_once_with("test")
            mock_shell.syscall.open_program.assert_called_once_with(
                "/programs/test.py"
            )

    def test_find_program_not_found(self, mock_shell: Any) -> None:
        """Test find_program when program is not found."""
        mock_syscall = MagicMock()
        mock_syscall.open_program.return_value = False
        mock_shell.syscall = mock_syscall

        with patch.object(
            mock_shell, "program_paths", return_value=["/programs/test.py"]
        ):
            result = mock_shell.find_program("test")
            assert result is False
