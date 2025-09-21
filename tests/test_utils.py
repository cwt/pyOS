from unittest.mock import MagicMock

import kernel.utils as utils
import kernel.common as common


class TestParser:

    def test_parser_initialization(self) -> None:
        """Test Parser initialization."""
        parser = utils.Parser("test_program", name="Test Program")
        assert parser.prog == "test_program"
        assert parser.name == "Test Program"
        assert parser.help is False

    def test_parser_default_name(self) -> None:
        """Test Parser initialization with default name."""
        parser = utils.Parser("test_program")
        assert parser.prog == "test_program"
        assert parser.name == "test_program"

    def test_add_shell(self) -> None:
        """Test adding shell to parser."""
        parser = utils.Parser("test_program")
        mock_shell = MagicMock()
        parser.add_shell(mock_shell)
        assert parser.shell == mock_shell

    def test_exit_override(self) -> None:
        """Test that exit method does nothing."""
        parser = utils.Parser("test_program")
        # Should not raise any exception
        parser.exit()

    def test_print_usage(self) -> None:
        """Test print_usage method."""
        parser = utils.Parser("test_program")
        mock_shell = MagicMock()
        parser.add_shell(mock_shell)
        parser.print_usage()
        assert parser.help is True
        mock_shell.stderr.write.assert_called_once()

    def test_print_help(self) -> None:
        """Test print_help method."""
        parser = utils.Parser("test_program")
        mock_shell = MagicMock()
        parser.add_shell(mock_shell)
        parser.print_help()
        assert parser.help is True
        mock_shell.stdout.write.assert_called_once()

    def test_help_msg(self) -> None:
        """Test help_msg method."""
        parser = utils.Parser("test_program", name="Test Program")
        msg = parser.help_msg()
        assert "Test Program" in msg


class TestPermissionUtils:

    def test_calc_permission_string(self) -> None:
        """Test permission string calculation."""
        # Test 777 -> rwxrwxrwx
        result = utils.calc_permission_string(777)
        assert result == "rwxrwxrwx"

        # Test 644 -> rw-r--r--
        result = utils.calc_permission_string(644)
        assert result == "rw-r--r--"

        # Test 755 -> rwxr-xr-x
        result = utils.calc_permission_string(755)
        assert result == "rwxr-xr-x"

    def test_calc_permission_number(self) -> None:
        """Test permission number calculation."""
        # Test rwxrwxrwx -> 777
        result = utils.calc_permission_number("rwxrwxrwx")
        assert result == "777"

        # Test rw-r--r-- -> 644
        result = utils.calc_permission_number("rw-r--r--")
        assert result == "644"

        # Test rwxr-xr-x -> 755
        result = utils.calc_permission_number("rwxr-xr-x")
        assert result == "755"

    def test_check_permission(self) -> None:
        """Test permission checking."""
        # Test user permissions
        assert utils.check_permission("rwxrwxrwx", "u", "r") is True
        assert utils.check_permission("rwxrwxrwx", "u", "w") is True
        assert utils.check_permission("rwxrwxrwx", "u", "x") is True

        # Test group permissions
        assert utils.check_permission("rwxrwxrwx", "g", "r") is True
        assert utils.check_permission("rwxrwxrwx", "g", "w") is True
        assert utils.check_permission("rwxrwxrwx", "g", "x") is True

        # Test other permissions
        assert utils.check_permission("rwxrwxrwx", "o", "r") is True
        assert utils.check_permission("rwxrwxrwx", "o", "w") is True
        assert utils.check_permission("rwxrwxrwx", "o", "x") is True

        # Test no permissions
        assert utils.check_permission("---------", "u", "r") is False
        assert utils.check_permission("---------", "g", "w") is False
        assert utils.check_permission("---------", "o", "x") is False


class TestConvertMany:

    def test_convert_many_single_value(self) -> None:
        """Test convert_many with single value."""
        result = utils.convert_many("test", "arg1", "arg2")
        assert result == [("test", "arg1", "arg2")]

    def test_convert_many_list(self) -> None:
        """Test convert_many with list."""
        result = utils.convert_many(["a", "b", "c"], "arg1", "arg2")
        assert result == [
            ("a", "arg1", "arg2"),
            ("b", "arg1", "arg2"),
            ("c", "arg1", "arg2"),
        ]

    def test_convert_many_tuple(self) -> None:
        """Test convert_many with tuple."""
        result = utils.convert_many(("a", "b", "c"), "arg1", "arg2")
        assert result == [
            ("a", "arg1", "arg2"),
            ("b", "arg1", "arg2"),
            ("c", "arg1", "arg2"),
        ]


class TestCommonUtils:

    def test_resolve_path(self) -> None:
        """Test resolve_path function."""
        mock_shell = MagicMock()
        mock_shell.sabs_path.return_value = "/absolute/path"
        result = common.resolve_path(mock_shell, "relative/path")
        assert result == "/absolute/path"
        mock_shell.sabs_path.assert_called_once_with("relative/path")

    def test_handle_file_operation_open(self) -> None:
        """Test handle_file_operation for open."""
        mock_shell = MagicMock()
        mock_shell.syscall.open_file.return_value = "file_object"
        result = common.handle_file_operation(
            mock_shell, "/test/file.txt", "open", "r"
        )
        assert result == "file_object"
        mock_shell.syscall.open_file.assert_called_once_with(
            "/test/file.txt", "r"
        )

    def test_handle_file_operation_exists(self) -> None:
        """Test handle_file_operation for exists."""
        mock_shell = MagicMock()
        mock_shell.syscall.exists.return_value = True
        result = common.handle_file_operation(
            mock_shell, "/test/file.txt", "exists"
        )
        assert result is True
        mock_shell.syscall.exists.assert_called_once_with("/test/file.txt")

    def test_handle_file_operation_is_file(self) -> None:
        """Test handle_file_operation for is_file."""
        mock_shell = MagicMock()
        mock_shell.syscall.is_file.return_value = True
        result = common.handle_file_operation(
            mock_shell, "/test/file.txt", "is_file"
        )
        assert result is True
        mock_shell.syscall.is_file.assert_called_once_with("/test/file.txt")

    def test_handle_file_operation_is_dir(self) -> None:
        """Test handle_file_operation for is_dir."""
        mock_shell = MagicMock()
        mock_shell.syscall.is_dir.return_value = True
        result = common.handle_file_operation(mock_shell, "/test/dir", "is_dir")
        assert result is True
        mock_shell.syscall.is_dir.assert_called_once_with("/test/dir")

    def test_handle_file_operation_remove(self) -> None:
        """Test handle_file_operation for remove."""
        mock_shell = MagicMock()
        mock_shell.syscall.remove.return_value = None
        result = common.handle_file_operation(
            mock_shell, "/test/file.txt", "remove"
        )
        assert result is None
        mock_shell.syscall.remove.assert_called_once_with("/test/file.txt")

    def test_handle_file_operation_error(self) -> None:
        """Test handle_file_operation with error."""
        mock_shell = MagicMock()
        mock_shell.syscall.open_file.side_effect = IOError("File not found")
        result = common.handle_file_operation(
            mock_shell, "/test/file.txt", "open", "r"
        )
        assert result is None
        mock_shell.stderr.write.assert_called_once()

    def test_process_stdin(self) -> None:
        """Test process_stdin function."""
        mock_shell = MagicMock()
        mock_shell.stdin.read.return_value = ["line1\n", "line2\n"]

        processed_lines = []

        def processor_func(line: str) -> None:
            processed_lines.append(line.rstrip())

        common.process_stdin(mock_shell, processor_func)

        assert processed_lines == ["line1", "line2"]

    def test_write_output_lines(self) -> None:
        """Test write_output_lines function."""
        mock_shell = MagicMock()
        lines = ["line1\n", "line2\n", ""]
        common.write_output_lines(mock_shell, lines)
        assert mock_shell.stdout.write.call_count == 3

    def test_validate_paths(self) -> None:
        """Test validate_paths function."""
        mock_shell = MagicMock()
        mock_shell.sabs_path.side_effect = lambda x: f"/absolute/{x}"
        mock_shell.syscall.exists.side_effect = (
            lambda x: x == "/absolute/valid.txt"
        )

        valid_paths, invalid_paths = common.validate_paths(
            mock_shell, ["valid.txt", "invalid.txt"]
        )

        assert valid_paths == ["/absolute/valid.txt"]
        assert invalid_paths == ["invalid.txt"]
        mock_shell.stderr.write.assert_called_once()

    def test_get_file_metadata(self) -> None:
        """Test get_file_metadata function."""
        mock_shell = MagicMock()
        mock_shell.syscall.get_meta_data.return_value = (
            "path",
            "owner",
            "perm",
            "created",
            "accessed",
            "modified",
        )
        result = common.get_file_metadata(mock_shell, "/test/file.txt")
        assert result == (
            "path",
            "owner",
            "perm",
            "created",
            "accessed",
            "modified",
        )
        mock_shell.syscall.get_meta_data.assert_called_once_with(
            "/test/file.txt"
        )

    def test_copy_file_metadata(self) -> None:
        """Test copy_file_metadata function."""
        mock_shell = MagicMock()
        mock_shell.syscall.get_meta_data.return_value = (
            "/test/src.txt",
            "root",
            "rwxrwxrwx",
            "created",
            "accessed",
            "modified",
        )
        common.copy_file_metadata(mock_shell, "/test/src.txt", "/test/dst.txt")

        mock_shell.syscall.set_owner.assert_called_once_with(
            "/test/dst.txt", "root"
        )
        mock_shell.syscall.set_permission.assert_called_once_with(
            "/test/dst.txt", "rwxrwxrwx"
        )
        mock_shell.syscall.set_time.assert_called_once()
