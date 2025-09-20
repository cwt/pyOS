from typing import Any, List


def run(shell: Any, args: List[str]) -> None:
    if args:
        path = shell.sabs_path(args[0])
        try:
            if args[1] in ("a", "w"):
                mode = args[1]
            else:
                shell.stderr.write("%s is not a valid file mode" % (args[1]))
        except IndexError:
            mode = "w"
        try:
            f = shell.syscall.open_file(path, mode)
            for line in shell.stdin.read():
                f.write("%s\n" % (line,))
            f.close()
        except Exception:
            shell.stderr.write("file error")
    else:
        shell.stderr.write("missing file operand")


def help() -> str:
    a = """
    Write

    Writes the stdin to a file at the given path.

    usage: write [path] [mode]
    """
    return a
