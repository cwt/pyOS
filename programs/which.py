from typing import Any, List


def run(shell: Any, args: List[str]) -> None:
    if args:
        for x in shell.program_paths(args[0]):
            program = shell.syscall.open_program(x)
            if program:
                shell.stdout.write(x)
                break


def help() -> str:
    a = """
    Which

    Prints the location of the program to be used.

    usage: which [program]
    """
    return a
