"""
Base command implementation for pyOS.
"""

from abc import ABC, abstractmethod
from typing import List, Any
from kernel.interfaces import CommandInterface


class BaseCommand(CommandInterface, ABC):
    """Base implementation of the CommandInterface."""

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__(name, description)

    @abstractmethod
    def run(self, shell: Any, args: List[str]) -> None:
        """Execute the command with the given arguments."""
        pass

    @abstractmethod
    def help(self) -> str:
        """Return help text for the command."""
        pass


class BaseFileCommand(BaseCommand):
    """Base implementation for file-based commands."""

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__(name, description)
        self.supports_stdin = True

    @abstractmethod
    def process_file(self, shell: Any, filepath: str) -> None:
        """Process a single file."""
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
        """Process input from stdin."""
        if shell.stdin:
            for line in shell.stdin.read():
                shell.stdout.write(line.rstrip())
