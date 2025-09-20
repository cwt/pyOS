from typing import Any, List


def run(shell: Any, args: List[str]) -> None:
    shell.stdout.write(" ".join(args))
    if not shell.stdout:
        shell.stdout.write("")


def help() -> str:
    a = """
    Echo

    Writes the arguments into the stdout.

    usage: echo [args]
    """
    return a
