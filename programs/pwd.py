from typing import Any, List
from kernel.io_utils import write_output


def run(shell: Any, args: List[str]) -> None:
    write_output(shell, shell.path)


def help() -> str:
    a = """
    Print Working Directory

    Prints the path of the current directory.

    usage: pwd
    """
    return a
