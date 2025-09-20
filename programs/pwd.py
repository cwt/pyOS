from typing import Any, List


def run(shell: Any, args: List[str]) -> None:
    shell.stdout.write(shell.get_path())


def help() -> str:
    a = """
    Print Working Directory

    Prints the path of the current directory.

    usage: pwd
    """
    return a
