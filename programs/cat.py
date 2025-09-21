from typing import Any, List
from kernel.base_command import BaseFileCommand
from kernel.common import resolve_path, handle_file_operation


class CatCommand(BaseFileCommand):
    """Concatenate files and print to stdout."""

    def __init__(self) -> None:
        super().__init__("cat", "Concatenate files and print to stdout")

    def process_file(self, shell: Any, filepath: str) -> None:
        """Process a single file."""
        path = resolve_path(shell, filepath)
        f = handle_file_operation(shell, path, "open", "r")
        if f:
            for line in f:
                shell.stdout.write(line.rstrip())
            f.close()

    def help(self) -> str:
        return """
    Concatenate

    Concatenate the files at the given paths.

    usage: cat [path]
    """


# Create a singleton instance for backward compatibility
command = CatCommand()


def run(shell: Any, args: List[str]) -> None:
    """Backward compatibility function."""
    command.run(shell, args)


def help() -> str:
    """Backward compatibility function."""
    return command.help()
