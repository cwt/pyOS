from kernel.utils import Parser
from typing import Any, List
from kernel.base_command import BaseFileCommand
from kernel.common import resolve_path, handle_file_operation


class CatCommand(BaseFileCommand):
    """Concatenate files and print to stdout."""

    def __init__(self) -> None:
        super().__init__("cat", "Concatenate files and print to stdout")
        self.parser = Parser(
            "cat",
            name="Concatenate",
            description="Concatenate the files at the given paths.",
        )
        pa = self.parser.add_argument
        pa("paths", type=str, nargs="*")
        pa("-n", "--number", action="store_true", dest="number", default=False)

    def run(self, shell: Any, args: List[str]) -> None:
        self.parser.add_shell(shell)
        parsed_args = self.parser.parse_args(args)
        if not self.parser.help:
            if parsed_args.paths or (shell.stdin and self.supports_stdin):
                # Process file arguments
                for path in parsed_args.paths:
                    self.process_file(shell, path, parsed_args.number)

                # Process stdin if available
                if shell.stdin and self.supports_stdin:
                    self.process_stdin(shell, parsed_args.number)
            else:
                shell.stderr.write("missing file operand")

    def process_file(
        self, shell: Any, filepath: str, number_lines: bool = False
    ) -> None:
        """Process a single file."""
        path = resolve_path(shell, filepath)
        f = handle_file_operation(shell, path, "open", "r")
        if f:
            line_num = 1
            for line in f:
                if number_lines:
                    shell.stdout.write(f"{line_num:6}  {line}")
                    line_num += 1
                else:
                    shell.stdout.write(line.rstrip())
            f.close()

    def process_stdin(self, shell: Any, number_lines: bool = False) -> None:
        """Process input from stdin."""
        if shell.stdin:
            line_num = 1
            for line in shell.stdin.read():
                if number_lines:
                    shell.stdout.write(f"{line_num:6}  {line}")
                    line_num += 1
                else:
                    shell.stdout.write(line.rstrip())

    def help(self) -> str:
        return """
    Concatenate

    Concatenate the files at the given paths.

    usage: cat [options] [path]

    Options:
      -n, --number    Number all output lines
    """


# Create a singleton instance for backward compatibility
command = CatCommand()


def run(shell: Any, args: List[str]) -> None:
    """Backward compatibility function."""
    command.run(shell, args)


def help() -> str:
    """Backward compatibility function."""
    return command.help()
