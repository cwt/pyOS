"""
Path operation utilities for pyOS.
"""

from typing import Any


def resolve_absolute_path(shell: Any, path: str) -> str:
    """Resolve a path to its absolute form."""
    return shell.sabs_path(path)


def resolve_relative_path(shell: Any, path: str, base: str = None) -> str:
    """Resolve a path to its relative form."""
    if base is None:
        base = shell.get_path()
    return shell.srel_path(resolve_absolute_path(shell, path), base)


def join_paths(shell: Any, *paths: str) -> str:
    """Join multiple paths together."""
    return shell.syscall.join_path(*paths)


def get_basename(shell: Any, path: str) -> str:
    """Get the basename of a path."""
    return shell.syscall.base_name(path)


def get_dirname(shell: Any, path: str) -> str:
    """Get the directory name of a path."""
    return shell.syscall.dir_name(path)


def split_path(shell: Any, path: str) -> tuple:
    """Split a path into directory and basename."""
    return shell.syscall.split(path)


def is_absolute_path(path: str) -> bool:
    """Check if a path is absolute."""
    return path.startswith("/")


def normalize_path(path: str) -> str:
    """Normalize a path by removing redundant separators."""
    # Simple normalization - can be expanded as needed
    return path.replace("//", "/")
