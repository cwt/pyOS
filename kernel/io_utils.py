"""
Standard I/O utilities for pyOS programs.
"""

from typing import Any, List, Callable


def read_stdin_lines(shell: Any) -> List[str]:
    """
    Read all lines from standard input.

    Args:
        shell: The shell object

    Returns:
        List of lines from stdin
    """
    lines = []
    if shell.stdin:
        try:
            lines = list(shell.stdin.read())
        except Exception:
            pass
    return lines


def process_stdin_lines(
    shell: Any, processor_func: Callable[[str], None]
) -> None:
    """
    Process each line from standard input with a callback function.

    Args:
        shell: The shell object
        processor_func: Function to call for each line
    """
    if shell.stdin:
        try:
            for line in shell.stdin.read():
                processor_func(line)
        except Exception as e:
            shell.stderr.write(f"Error processing stdin: {str(e)}")


def write_output(shell: Any, content: str) -> None:
    """
    Write content to standard output.

    Args:
        shell: The shell object
        content: Content to write
    """
    if shell.stdout:
        shell.stdout.write(content)


def write_lines(shell: Any, lines: List[str]) -> None:
    """
    Write multiple lines to standard output.

    Args:
        shell: The shell object
        lines: List of lines to write
    """
    for line in lines:
        write_output(shell, line)


def write_error(shell: Any, error_msg: str) -> None:
    """
    Write error message to standard error.

    Args:
        shell: The shell object
        error_msg: Error message to write
    """
    if shell.stderr:
        shell.stderr.write(error_msg)
