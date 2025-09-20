from kernel.utils import Parser
from typing import Any, List
from kernel.common import (
    resolve_path,
    handle_file_operation,
    copy_file_metadata,
)


desc = "Copies the given file/directory to the given location."
parser = Parser("cp", name="Copy", description=desc)
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
        if len(args.paths) >= 2:
            dest = resolve_path(shell, args.paths[-1])
            if (
                handle_file_operation(shell, dest, "is_dir")
                or len(args.paths) == 2
                or not handle_file_operation(shell, dest, "exists")
            ):
                for src in args.paths[:-1]:
                    copy(shell, args, src, dest)
            else:
                shell.stderr.write("%s is not a directory" % dest)
        else:
            shell.stderr.write("missing file operand")


def copy(shell: Any, args: Any, src: str, dest: str) -> None:
    src = resolve_path(shell, src)

    if args.recursive and handle_file_operation(shell, src, "is_dir"):
        # This would need to be implemented in the common module if used frequently
        srcpaths = []

        def collect_paths(current_path):
            srcpaths.append(current_path)
            if handle_file_operation(shell, current_path, "is_dir"):
                for item in shell.syscall.list_dir(current_path):
                    item_path = shell.syscall.join_path(current_path, item)
                    collect_paths(item_path)

        collect_paths(src)
    else:
        srcpaths = [src]

    if handle_file_operation(shell, dest, "is_dir"):
        join = [dest, shell.syscall.base_name(src)]
        destbase = shell.syscall.join_path(*join)
    else:
        destbase = dest

    for path in srcpaths:
        relpath = shell.srel_path(path, src)
        if relpath != ".":
            destpath = shell.syscall.join_path(destbase, relpath)
        else:
            destpath = destbase

        if args.verbose:
            shell.stdout.write("Copying %s to %s" % (path, destpath))

        try:
            if handle_file_operation(shell, path, "is_dir"):
                if args.recursive:
                    copy_dir(shell, path, destpath)
                else:
                    shell.stdout.write("omitting directory: %s" % path)
            else:
                handle_file_operation(shell, path, "copy", destpath)
        except OSError:
            shell.stderr.write("file error " + destpath)


def copy_dir(shell: Any, src: str, dest: str) -> None:
    handle_file_operation(shell, dest, "make_dir")
    copy_file_metadata(shell, src, dest)


def help() -> str:
    return parser.help_msg()
