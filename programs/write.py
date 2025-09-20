from typing import Any, List
from kernel.common import resolve_path, handle_file_operation, process_stdin


def run(shell: Any, args: List[str]) -> None:
    if args:
        path = resolve_path(shell, args[0])
        try:
            if args[1] in ("a", "w"):
                mode = args[1]
            else:
                shell.stderr.write("%s is not a valid file mode" % (args[1]))
        except IndexError:
            mode = "w"
        f = handle_file_operation(shell, path, "open", mode)
        if f:

            def write_line(line):
                f.write("%s\n" % (line,))

            process_stdin(shell, write_line)
            f.close()
    else:
        shell.stderr.write("missing file operand")


def help() -> str:
    a = """
    Write

    Writes the stdin to a file at the given path.

    usage: write [path] [mode]
    """
    return a
