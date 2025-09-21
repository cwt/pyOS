"""
Common file operation utilities for pyOS programs.
"""

from typing import Any, List, Callable, Optional


def process_files_with_callback(
    shell: Any,
    paths: List[str],
    file_callback: Callable[[str], None],
    dir_callback: Optional[Callable[[str], None]] = None,
    recursive: bool = False,
) -> None:
    """
    Process a list of files with callback functions.

    Args:
        shell: The shell object
        paths: List of file paths to process
        file_callback: Function to call for each file
        dir_callback: Function to call for directories (optional)
        recursive: Whether to process directories recursively
    """
    for path in paths:
        abs_path = shell.sabs_path(path)
        if shell.syscall.is_dir(abs_path):
            if recursive:
                if dir_callback:
                    dir_callback(abs_path)
                # Process all items in the directory recursively
                items = shell.syscall.list_dir(abs_path)
                sub_paths = [
                    shell.syscall.join_path(abs_path, item) for item in items
                ]
                process_files_with_callback(
                    shell, sub_paths, file_callback, dir_callback, recursive
                )
            elif dir_callback:
                dir_callback(abs_path)
            else:
                shell.stderr.write(f"{path} is a directory")
        else:
            try:
                file_callback(abs_path)
            except IOError:
                shell.stderr.write(f"{path} does not exist")
            except Exception as e:
                shell.stderr.write(f"Error processing {path}: {str(e)}")


def read_file_lines(shell: Any, path: str) -> List[str]:
    """
    Read all lines from a file.

    Args:
        shell: The shell object
        path: Path to the file

    Returns:
        List of lines from the file
    """
    lines = []
    try:
        f = shell.syscall.open_file(path, "r")
        lines = f.readlines()
        f.close()
    except IOError:
        shell.stderr.write(f"{path} does not exist")
    except Exception as e:
        shell.stderr.write(f"Error reading {path}: {str(e)}")
    return lines


def write_lines_to_file(
    shell: Any, path: str, lines: List[str], mode: str = "w"
) -> bool:
    """
    Write lines to a file.

    Args:
        shell: The shell object
        path: Path to the file
        lines: List of lines to write
        mode: File mode ('w' for write, 'a' for append)

    Returns:
        True if successful, False otherwise
    """
    try:
        f = shell.syscall.open_file(path, mode)
        for line in lines:
            f.write(f"{line}\n")
        f.close()
        return True
    except Exception as e:
        shell.stderr.write(f"Error writing to {path}: {str(e)}")
        return False
