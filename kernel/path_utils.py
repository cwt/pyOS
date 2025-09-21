"""
Path operation utilities for pyOS.
"""

from typing import Any, Optional


def resolve_absolute_path(shell: Any, path: str) -> str:
    """Resolve a path to its absolute form."""
    result = shell.sabs_path(path)
    return str(result) if result is not None else path


def resolve_relative_path(
    shell: Any, path: str, base: Optional[str] = None
) -> str:
    """Resolve a path to its relative form."""
    if base is None:
        base = shell.path
    result = shell.srel_path(resolve_absolute_path(shell, path), base)
    return str(result) if result is not None else path


def join_paths(shell: Any, *paths: str) -> str:
    """Join multiple paths together."""
    result = shell.syscall.join_path(*paths)
    return str(result) if result is not None else ""


def get_basename(shell: Any, path: str) -> str:
    """Get the basename of a path."""
    result = shell.syscall.base_name(path)
    return str(result) if result is not None else ""


def get_dirname(shell: Any, path: str) -> str:
    """Get the directory name of a path."""
    result = shell.syscall.dir_name(path)
    return str(result) if result is not None else ""


def split_path(shell: Any, path: str) -> tuple[str, str]:
    """Split a path into directory and basename."""
    result = shell.syscall.split(path)
    if result is not None and isinstance(result, tuple) and len(result) >= 2:
        return (
            str(result[0]) if result[0] is not None else "",
            str(result[1]) if result[1] is not None else "",
        )
    return ("", "")


def is_absolute_path(path: str) -> bool:
    """Check if a path is absolute."""
    return path.startswith("/")


def normalize_path(path: str) -> str:
    """Normalize a path by removing redundant separators."""
    # Simple normalization - can be expanded as needed
    return path.replace("//", "/")
