from kernel.utils import Parser
from typing import Any, List
from kernel.common import resolve_path, handle_file_operation


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
    path = resolve_path(shell, path)

    if handle_file_operation(shell, path, "is_dir"):
        if args.recursive:
            paths = []

            def collect_paths(current_path):
                paths.append(current_path)
                if handle_file_operation(shell, current_path, "is_dir"):
                    for item in shell.syscall.list_dir(current_path):
                        item_path = shell.syscall.join_path(current_path, item)
                        collect_paths(item_path)

            collect_paths(path)
        else:
            shell.stderr.write("%s is a directory" % (path,))
            return
    else:
        paths = [path]

    for p in reversed(paths):
        if args.verbose:
            shell.stdout.write("Removing %s" % (p,))
        try:
            if handle_file_operation(shell, p, "is_dir"):
                handle_file_operation(shell, p, "remove_dir")
            else:
                handle_file_operation(shell, p, "remove")
        except OSError:
            shell.stderr.write("%s does not exist" % (p,))


def help() -> str:
    return parser.help_msg()
