from typing import Any, List
from kernel.common import resolve_path, handle_file_operation, process_stdin


def run(shell: Any, args: List[str]) -> None:
    if args or shell.stdin:
        for x in args:
            path = resolve_path(shell, x)
            f = handle_file_operation(shell, path, "open", "r")
            if f:
                for line in f:
                    shell.stdout.write(line.rstrip())
                f.close()
        if shell.stdin:

            def write_line(line):
                shell.stdout.write(line.rstrip())

            process_stdin(shell, write_line)
    else:
        shell.stderr.write("missing file operand")


def help() -> str:
    a = """
    Concatenate

    Concatenate the files at the given paths.

    usage: cat [path]
    """
    return a
