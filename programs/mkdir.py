from kernel.utils import Parser
from typing import Any, List
from kernel.common import resolve_path, handle_file_operation
from kernel.io_utils import write_output, write_error


desc = "Creates a directory at the given path."
parser = Parser("mkdir", name="Make Directory", description=desc)
pa = parser.add_argument
pa(
    "paths",
    type=str,
    nargs="*",
)
pa("-p", action="store_true", dest="parent", default=False)
pa("-v", action="store_true", dest="verbose", default=False)


def run(shell: Any, args: List[str]) -> None:
    parser.add_shell(shell)
    args = parser.parse_args(args)
    if not parser.help:
        if args.paths:
            for path in args.paths:
                make_dir(shell, args, path)
        else:
            write_error(shell, "missing directory operand")


def make_dir(shell: Any, args: Any, path: str) -> None:
    path = resolve_path(shell, path)
    if not handle_file_operation(shell, path, "exists"):
        paths = []
        if args.parent:
            while True:
                paths.append(path)
                path = shell.syscall.dir_name(path)
                if handle_file_operation(shell, path, "is_dir"):
                    break
        else:
            paths.append(path)
        for x in reversed(paths):
            if args.verbose:
                write_output(shell, "Making directory: %s" % (path,))
            try:
                handle_file_operation(shell, x, "make_dir")
            except IOError:
                write_error(shell, "could not make directory %s" % (path,))
                break
                # TODO # delete on fail?
    else:
        write_error(shell, "%s already exists" % (path,))


def help() -> str:
    return parser.help_msg()
