from typing import Any, List
from kernel.common import resolve_path, handle_file_operation
from kernel.io_utils import write_error


def run(shell: Any, args: List[str]) -> None:
    # hack to fix encapsulation
    shell = shell.parent
    if args:
        path = resolve_path(shell, args[0])
        if handle_file_operation(shell, path, "is_dir"):
            shell.set_path(path)
        else:
            write_error(shell, "%s: no such directory" % (path,))


def help() -> str:
    a = """
    Change Directory

    Changes the current directory.

    usage: cd [path]
    """
    return a
