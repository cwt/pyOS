"""
Custom exceptions for pyOS.
"""

from typing import Optional


class PyOSError(Exception):
    """Base exception for pyOS errors."""

    pass


class FileNotFoundError(PyOSError):
    """Raised when a file is not found."""

    def __init__(self, path: str, message: Optional[str] = None):
        self.path = path
        if message is None:
            message = f"File not found: {path}"
        super().__init__(message)


class PermissionDeniedError(PyOSError):
    """Raised when permission is denied for an operation."""

    def __init__(
        self, path: str, operation: str, message: Optional[str] = None
    ):
        self.path = path
        self.operation = operation
        if message is None:
            message = f"Permission denied: {operation} on {path}"
        super().__init__(message)


class DirectoryNotEmptyError(PyOSError):
    """Raised when trying to remove a non-empty directory."""

    def __init__(self, path: str, message: Optional[str] = None):
        self.path = path
        if message is None:
            message = f"Directory not empty: {path}"
        super().__init__(message)


class InvalidPathError(PyOSError):
    """Raised when a path is invalid."""

    def __init__(self, path: str, message: Optional[str] = None):
        self.path = path
        if message is None:
            message = f"Invalid path: {path}"
        super().__init__(message)


class CommandNotFoundError(PyOSError):
    """Raised when a command is not found."""

    def __init__(self, command: str, message: Optional[str] = None):
        self.command = command
        if message is None:
            message = f"Command not found: {command}"
        super().__init__(message)
