import pytest
from unittest.mock import patch, MagicMock
from typing import Generator, Any

import kernel.system as system
from kernel.constants import SystemState


class TestSystem:

    @pytest.fixture(autouse=True)
    def reset_system(self) -> Generator[None, None, None]:
        """Reset the System singleton before each test."""
        # Since System is no longer a singleton, we just create a new instance
        yield
        # No cleanup needed since we create new instances

    def test_system_initialization(self) -> None:
        """Test system initialization."""
        sys = system.System()

        assert sys.state == SystemState.IDLE
        assert sys.pids == []
        assert hasattr(sys, "filesystem")
        assert hasattr(sys, "metadata")
        assert hasattr(sys, "userdata")

    def test_new_pid(self) -> None:
        """Test PID assignment."""
        sys = system.System()

        mock_process = MagicMock()
        pid = sys.new_pid(mock_process)
        assert pid == 0
        assert len(sys.pids) == 1
        assert sys.pids[0] == mock_process

    def test_get_pid(self) -> None:
        """Test PID retrieval."""
        sys = system.System()

        mock_process = MagicMock()
        sys.new_pid(mock_process)

        pid = sys.get_pid(mock_process)
        assert pid == 0

        # Test non-existent process
        non_existent = MagicMock()
        pid = sys.get_pid(non_existent)
        assert pid is None

    def test_get_process(self) -> None:
        """Test process retrieval by PID."""
        sys = system.System()

        mock_process = MagicMock()
        sys.new_pid(mock_process)

        process = sys.get_process(0)
        assert process == mock_process

        # Test non-existent PID
        process = sys.get_process(999)
        assert process is None

    def test_kill(self) -> None:
        """Test process termination."""
        sys = system.System()

        mock_process = MagicMock()
        sys.new_pid(mock_process)
        assert len(sys.pids) == 1

        sys.kill(mock_process)
        assert len(sys.pids) == 0

    def test_new_shell(self) -> None:
        """Test shell creation."""
        sys = system.System()

        with patch("kernel.shell.Shell") as mock_shell_class:
            mock_shell_instance = MagicMock()
            mock_shell_class.return_value = mock_shell_instance

            shell_instance = sys.new_shell(program="test")

            # Check that Shell was instantiated with correct arguments
            mock_shell_class.assert_called_once()
            args, kwargs = mock_shell_class.call_args
            assert args == (0,)
            assert kwargs["program"] == "test"
            assert "system_instance" in kwargs
            assert shell_instance == mock_shell_instance
            assert sys.state == SystemState.RUNNING

    @patch("kernel.filesystem.open_program")
    def test_startup(self, mock_open_program: Any) -> None:
        """Test system startup."""
        sys = system.System()

        mock_program = MagicMock()
        mock_open_program.return_value = mock_program

        sys.startup()

        # Check that startup program was opened and run
        mock_open_program.assert_called_once()
        mock_program.run.assert_called_once()

    @patch("kernel.filesystem.open_program")
    def test_shutdown(self, mock_open_program: Any) -> None:
        """Test system shutdown."""
        sys = system.System()

        mock_program = MagicMock()
        mock_open_program.return_value = mock_program

        sys.shutdown()

        # Check that shutdown program was opened and run
        mock_open_program.assert_called_once()
        mock_program.run.assert_called_once()


class TestSysCall:

    @pytest.fixture
    def mock_shell(self) -> Any:
        """Create a mock shell."""
        return MagicMock()

    @pytest.fixture
    def syscall(self, mock_shell: Any) -> Any:
        """Create a SysCall instance."""
        return system.SysCall(mock_shell)

    def test_syscall_initialization(
        self, syscall: Any, mock_shell: Any
    ) -> None:
        """Test SysCall initialization."""
        assert syscall.shell == mock_shell
        assert hasattr(syscall, "fs_service")
        assert hasattr(syscall, "md_service")
        assert hasattr(syscall, "ud_service")

    # Test path-related methods
    def test_abs_path(self, syscall: Any) -> None:
        """Test absolute path method."""
        syscall.fs_service.abs_path = MagicMock(return_value="/absolute/path")
        result = syscall.abs_path("relative/path")
        assert result == "/absolute/path"
        syscall.fs_service.abs_path.assert_called_once_with("relative/path")

    def test_join_path(self, syscall: Any) -> None:
        """Test path joining method."""
        syscall.fs_service.join_path = MagicMock(return_value="/path/joined")
        result = syscall.join_path("path", "joined")
        assert result == "/path/joined"
        syscall.fs_service.join_path.assert_called_once_with("path", "joined")

    # Test file operation methods (with permission checking)
    @patch(
        "kernel.permissions.PermissionChecker._has_permission",
        return_value=True,
    )
    def test_exists(self, mock_has_permission: Any, syscall: Any) -> None:
        """Test exists method."""
        syscall.fs_service.exists = MagicMock(return_value=True)
        result = syscall.exists("/test/path")
        assert result is True
        syscall.fs_service.exists.assert_called_once_with("/test/path")

    @patch(
        "kernel.permissions.PermissionChecker._has_permission",
        return_value=True,
    )
    def test_is_file(self, mock_has_permission: Any, syscall: Any) -> None:
        """Test is_file method."""
        syscall.fs_service.is_file = MagicMock(return_value=True)
        result = syscall.is_file("/test/file.txt")
        assert result is True
        syscall.fs_service.is_file.assert_called_once_with("/test/file.txt")

    @patch(
        "kernel.permissions.PermissionChecker._has_permission",
        return_value=True,
    )
    def test_is_dir(self, mock_has_permission: Any, syscall: Any) -> None:
        """Test is_dir method."""
        syscall.fs_service.is_dir = MagicMock(return_value=True)
        result = syscall.is_dir("/test/dir")
        assert result is True
        syscall.fs_service.is_dir.assert_called_once_with("/test/dir")

    @patch(
        "kernel.permissions.PermissionChecker._has_permission",
        return_value=True,
    )
    def test_remove(self, mock_has_permission: Any, syscall: Any) -> None:
        """Test remove method."""
        syscall.fs_service.remove = MagicMock()
        syscall.md_service.delete_path = MagicMock()
        syscall.remove("/test/file.txt")
        syscall.fs_service.remove.assert_called_once_with("/test/file.txt")
        syscall.md_service.delete_path.assert_called_once_with("/test/file.txt")

    @patch(
        "kernel.permissions.PermissionChecker._has_permission",
        return_value=True,
    )
    def test_make_dir(self, mock_has_permission: Any, syscall: Any) -> None:
        """Test make_dir method."""
        syscall.fs_service.make_dir = MagicMock()
        syscall.md_service.add_path = MagicMock()
        syscall.make_dir("/test/newdir")
        syscall.fs_service.make_dir.assert_called_once_with("/test/newdir")
        syscall.md_service.add_path.assert_called_once_with(
            "/test/newdir", "root", "rwxrwxrwx"
        )

    # Test metadata methods (with permission checking)
    @patch(
        "kernel.permissions.PermissionChecker._has_permission",
        return_value=True,
    )
    def test_get_owner(self, mock_has_permission: Any, syscall: Any) -> None:
        """Test get_owner method."""
        syscall.md_service.get_owner = MagicMock(return_value="root")
        result = syscall.get_owner("/test/file.txt")
        assert result == "root"
        syscall.md_service.get_owner.assert_called_once_with("/test/file.txt")

    @patch(
        "kernel.permissions.PermissionChecker._has_permission",
        return_value=True,
    )
    def test_get_permission_string(
        self, mock_has_permission: Any, syscall: Any
    ) -> None:
        """Test get_permission_string method."""
        syscall.md_service.get_permission_string = MagicMock(
            return_value="rwxrwxrwx"
        )
        result = syscall.get_permission_string("/test/file.txt")
        assert result == "rwxrwxrwx"
        syscall.md_service.get_permission_string.assert_called_once_with(
            "/test/file.txt"
        )

    # Test user data methods
    @patch("kernel.userdata.correct_password")
    def test_correct_password(
        self, mock_correct_password: Any, syscall: Any
    ) -> None:
        """Test correct_password method."""
        mock_correct_password.return_value = True
        result = syscall.correct_password("user", "password")
        assert result is True
        mock_correct_password.assert_called_once_with("user", "password")

    @patch("kernel.userdata.get_user_data")
    def test_get_user_data(self, mock_get_user_data: Any, syscall: Any) -> None:
        """Test get_user_data method."""
        mock_get_user_data.return_value = (
            "user",
            "group",
            "info",
            "/home",
            "/shell",
            "password",
        )
        result = syscall.get_user_data("user")
        assert result == (
            "user",
            "group",
            "info",
            "/home",
            "/shell",
            "password",
        )
        mock_get_user_data.assert_called_once_with("user")


class TestFileDecorator:

    def test_file_decorator_initialization(self) -> None:
        """Test FileDecorator initialization."""
        mock_file = MagicMock()

        # Mock the System singleton's metadata
        with patch.object(system.System, "metadata", new_callable=MagicMock):
            decorator = system.FileDecorator(mock_file, "test.txt")
            assert decorator._FileDecorator__f == mock_file
            assert decorator._FileDecorator__name == "test.txt"

    def test_file_decorator_close(self) -> None:
        """Test FileDecorator close method."""
        mock_file = MagicMock()

        # Mock the System singleton's metadata
        with patch.object(
            system.System, "metadata", new_callable=MagicMock
        ) as mock_metadata:
            decorator = system.FileDecorator(mock_file, "test.txt")
            # Clear the call history from initialization
            mock_metadata.set_time.reset_mock()
            decorator.close()

            # Check that metadata.set_time was called with the right parameters
            mock_metadata.set_time.assert_called_once_with("test.txt", "mn")
            # Check that the underlying file's close method was called
            mock_file.close.assert_called_once()

    def test_file_decorator_name_property(self) -> None:
        """Test FileDecorator name property."""
        mock_file = MagicMock()

        # Mock the System singleton's metadata
        with patch.object(system.System, "metadata", new_callable=MagicMock):
            decorator = system.FileDecorator(mock_file, "test.txt")
            assert decorator.name == "test.txt"

    def test_file_decorator_delegation(self) -> None:
        """Test FileDecorator method delegation."""
        mock_file = MagicMock()
        mock_file.test_method.return_value = "test_result"

        # Mock the System singleton's metadata
        with patch.object(system.System, "metadata", new_callable=MagicMock):
            decorator = system.FileDecorator(mock_file, "test.txt")
            result = decorator.test_method()

            # Check that the method was called on the underlying file
            mock_file.test_method.assert_called_once()
            assert result == "test_result"
