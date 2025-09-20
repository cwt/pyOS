from kernel.utils import Parser
from typing import Any, List


desc = "Removes the file/directory."
parser = Parser("rm", name="Remove", description=desc)
pa = parser.add_argument
pa(
    "paths",
    type=str,
    nargs="*",
)
pa("-f", action="store_true", dest="force", default=False)
pa("-r", action="store_true", dest="recursive", default=False)
pa("-v", action="store_true", dest="verbose", default=False)


def run(shell: Any, args: List[str]) -> None:
    parser.add_shell(shell)
    args = parser.parse_args(args)
    if not parser.help:
        if len(args.paths) >= 1:
            for path in args.paths:
                remove(shell, args, path)
        else:
            shell.stderr.write("missing file operand")


def remove(shell: Any, args: Any, path: str) -> None:
    path = shell.sabs_path(path)

    if shell.syscall.is_dir(path):
        if args.recursive:
            paths = shell.syscall.list_all(path)
        else:
            shell.stderr.write("%s is a directory" % (path,))
            return
    else:
        paths = [path]

    for p in reversed(paths):
        if args.verbose:
            shell.stdout.write("Removing %s" % (p,))
        try:
            if shell.syscall.is_dir(p):
                shell.syscall.remove_dir(p)
            else:
                shell.syscall.remove(p)
        except OSError:
            shell.stderr.write("%s does not exist" % (p,))


def help() -> str:
    return parser.help_msg()
