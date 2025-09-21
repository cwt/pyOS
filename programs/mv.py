import argparse
from kernel.utils import Parser
from typing import Any, List
from kernel.common import (
    resolve_path,
    handle_file_operation,
    copy_file_metadata,
)


desc = "Moves the given file/directory to the given location."
parser = Parser("mv", name="Move", description=desc)
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
    parsed_args = parser.parse_args(args)
    if not parser.help:
        if len(parsed_args.paths) >= 2:
            dest = resolve_path(shell, parsed_args.paths[-1])
            if (
                handle_file_operation(shell, dest, "is_dir")
                or len(parsed_args.paths) == 2
            ):
                for src in parsed_args.paths[:-1]:
                    move(shell, parsed_args, src, dest)
            else:
                shell.stderr.write("%s is not a directory" % (dest,))
        else:
            shell.stderr.write("missing file operand")


def move(shell: Any, args: argparse.Namespace, src: str, dest: str) -> None:
    src = resolve_path(shell, src)

    if handle_file_operation(shell, src, "is_dir"):
        srcpaths = []

        def collect_paths(current_path: str) -> None:
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

    copiedpaths = []
    for path in srcpaths:
        relpath = shell.srel_path(path, src)
        if relpath != ".":
            destpath = shell.syscall.join_path(destbase, relpath)
        else:
            destpath = destbase

        try:
            if handle_file_operation(shell, path, "is_dir"):
                copy_dir(shell, path, destpath)
            else:
                handle_file_operation(shell, path, "copy", destpath)
            copiedpaths.append(path)
        except OSError:
            shell.stderr.write("file error " + destpath)

    for path in reversed(copiedpaths):
        try:
            if handle_file_operation(shell, path, "is_dir"):
                handle_file_operation(shell, path, "remove_dir")
            else:
                handle_file_operation(shell, path, "remove")
        except OSError:
            shell.stderr.write("%s does not exist" % (path,))


def copy_dir(shell: Any, src: str, dest: str) -> None:
    handle_file_operation(shell, dest, "make_dir")
    copy_file_metadata(shell, src, dest)


def help() -> str:
    return parser.help_msg()
