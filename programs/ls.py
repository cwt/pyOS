from kernel.utils import Parser
from typing import Any, List
from kernel.common import resolve_path, handle_file_operation


desc = "Returns the contents of a directory."
parser = Parser("ls", name="List Directory", description=desc)
pa = parser.add_argument
pa(
    "paths",
    type=str,
    nargs="*",
)
pa("-l", action="store_true", dest="long", default=False)
pa("-a", action="store_true", dest="all", default=False)


def run(shell: Any, args: List[str]) -> None:
    parser.add_shell(shell)
    args = parser.parse_args(args)
    if not parser.help:
        if args.paths:
            paths = args.paths
        else:
            paths = [shell.get_path()]
        for relpath in sorted(paths):
            ls(shell, relpath, args)


def ls(shell: Any, relpath: str, args: Any) -> None:
    fsgm = shell.syscall.get_meta_data
    fsbn = shell.syscall.base_name
    format_str = "%s %s %s %s"
    path = resolve_path(shell, relpath)
    if handle_file_operation(shell, path, "exists"):
        try:
            a = shell.syscall.list_dir(path)
            if args.long:
                b = [
                    fsgm(resolve_path(shell, shell.syscall.join_path(path, x)))
                    for x in a
                ]
                # Unpack all 6 values from metadata: path, owner, permission, created, accessed, modified
                # Use the permission string directly since it's already in string format
                a = [
                    format_str % (perm, owner, "1", fsbn(name))
                    for name, owner, perm, _, _, _ in b
                ]

            if len(args.paths) > 1:
                shell.stdout.write("%s:" % (relpath,))
            if shell.stdout or args.long:
                shell.stdout.write("\n".join(a))
            else:
                if a:
                    maxlen = max(max([len(x) for x in a]), 1)
                    # arbitrary line length
                    columns = (80 // maxlen) - 1
                    b = []
                    for i, x in enumerate(a):
                        newline = "\n" if not ((i + 1) % columns) else ""
                        if not ((i + 1) % columns):
                            newline = "\n"
                            spacing = ""
                        else:
                            newline = ""
                            spacing = " " * (maxlen - len(x) + 1)
                        b.append(x + spacing + newline)
                    output = "".join(b).rstrip()
                    shell.stdout.write(output)
                    if output:  # Only add newline if there was output
                        shell.stdout.write("\n")
            if len(args.paths) > 1:
                shell.stdout.write("\n")
        except OSError:
            shell.stderr.write(
                "ls: cannot acces %s: no such file or directory\n" % (relpath,)
            )
    else:
        shell.stderr.write(
            "ls: cannot acces %s: no such file or directory\n" % (relpath,)
        )


def help() -> str:
    return parser.help_msg()
