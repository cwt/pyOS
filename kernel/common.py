"""
Common utility functions to eliminate code duplication across the pyOS project.
"""

from typing import Any, List, Optional, Tuple


def resolve_path(shell: Any, path: str) -> str:
    """Resolve a path to its absolute form using the shell's sabs_path method."""
    return shell.sabs_path(path)


def handle_file_operation(
    shell: Any, path: str, operation: str, *args, **kwargs
) -> Optional[Any]:
    """Generic file operation handler with error handling."""
    try:
        if operation == "open":
            return shell.syscall.open_file(path, *args)
        elif operation == "exists":
            return shell.syscall.exists(path)
        elif operation == "is_file":
            return shell.syscall.is_file(path)
        elif operation == "is_dir":
            return shell.syscall.is_dir(path)
        elif operation == "remove":
            return shell.syscall.remove(path)
        elif operation == "remove_dir":
            return shell.syscall.remove_dir(path)
        elif operation == "make_dir":
            return shell.syscall.make_dir(path)
        elif operation == "copy":
            return shell.syscall.copy(path, args[0])
        else:
            shell.stderr.write(f"Unknown file operation: {operation}")
            return None
    except IOError:
        shell.stderr.write(f"{path} does not exist")
        return None
    except OSError:
        shell.stderr.write(f"File error: {path}")
        return None
    except Exception as e:
        shell.stderr.write(f"Error with {path}: {str(e)}")
        return None


def process_stdin(shell: Any, processor_func: callable) -> None:
    """Generic stdin processing function."""
    if shell.stdin:
        for line in shell.stdin.read():
            processor_func(line)


def write_output_lines(shell: Any, lines: List[str]) -> None:
    """Write multiple lines to stdout."""
    for line in lines:
        shell.stdout.write(line.rstrip() if line else "")


def validate_paths(
    shell: Any, paths: List[str], must_exist: bool = True
) -> Tuple[List[str], List[str]]:
    """Validate a list of paths and separate valid from invalid ones."""
    valid_paths = []
    invalid_paths = []

    for path in paths:
        abs_path = resolve_path(shell, path)
        if handle_file_operation(shell, abs_path, "exists"):
            valid_paths.append(abs_path)
        else:
            invalid_paths.append(path)
            if must_exist:
                shell.stderr.write(f"{path} does not exist")

    return valid_paths, invalid_paths


def get_file_metadata(shell: Any, path: str) -> Optional[Tuple]:
    """Get metadata for a file."""
    try:
        return shell.syscall.get_meta_data(path)
    except Exception:
        return None


def copy_file_metadata(shell: Any, src_path: str, dest_path: str) -> None:
    """Copy metadata from source to destination file."""
    try:
        meta = shell.syscall.get_meta_data(src_path)
        if meta:
            shell.syscall.set_owner(dest_path, meta[1])
            shell.syscall.set_permission(dest_path, meta[2])
            shell.syscall.set_time(dest_path, meta[3:6])
    except Exception:
        pass  # Silently fail if metadata can't be copied
