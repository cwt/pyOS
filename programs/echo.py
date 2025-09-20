from typing import Any, List
from kernel.io_utils import write_output


def run(shell: Any, args: List[str]) -> None:
    write_output(shell, " ".join(args))
    if not shell.stdout:
        write_output(shell, "")


def help() -> str:
    a = """
    Echo

    Writes the arguments into the stdout.

    usage: echo [args]
    """
    return a
