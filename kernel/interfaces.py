"""
Abstract base classes for command interfaces in pyOS.
"""

from abc import ABC, abstractmethod
from typing import List, Any


class CommandInterface(ABC):
    """Abstract base class for all commands in pyOS."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, shell: Any, args: List[str]) -> None:
        """Execute the command with the given arguments.

        Args:
            shell: The shell instance executing the command
            args: List of command arguments
        """
        pass

    @abstractmethod
    def help(self) -> str:
        """Return help text for the command.

        Returns:
            Help text as a string
        """
        pass


class FileCommandInterface(CommandInterface):
    """Abstract base class for file-based commands."""

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__(name, description)
        self.supports_stdin = True

    @abstractmethod
    def process_file(self, shell: Any, filepath: str) -> None:
        """Process a single file.

        Args:
            shell: The shell instance
            filepath: Path to the file to process
        """
        pass

    def run(self, shell: Any, args: List[str]) -> None:
        """Default implementation for file-based commands."""
        if args or (shell.stdin and self.supports_stdin):
            # Process file arguments
            for arg in args:
                self.process_file(shell, arg)

            # Process stdin if available
            if shell.stdin and self.supports_stdin:
                self.process_stdin(shell)
        else:
            shell.stderr.write("missing file operand")

    def process_stdin(self, shell: Any) -> None:
        """Process input from stdin.

        Args:
            shell: The shell instance
        """
        if shell.stdin:
            for line in shell.stdin.read():
                shell.stdout.write(line.rstrip())


class DirectoryCommandInterface(CommandInterface):
    """Abstract base class for directory-based commands."""

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__(name, description)

    @abstractmethod
    def process_directory(
        self, shell: Any, dirpath: str, recursive: bool = False
    ) -> None:
        """Process a directory.

        Args:
            shell: The shell instance
            dirpath: Path to the directory to process
            recursive: Whether to process subdirectories recursively
        """
        pass
