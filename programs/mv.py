from kernel.utils import Parser
from typing import Any, List


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
    args = parser.parse_args(args)
    if not parser.help:
        if len(args.paths) >= 2:
            dest = shell.sabs_path(args.paths[-1])
            if shell.syscall.is_dir(dest) or len(args.paths) == 2:
                for src in args.paths[:-1]:
                    move(shell, args, src, dest)
            else:
                shell.stderr.write("%s is not a directory" % (dest,))
        else:
            shell.stderr.write("missing file operand")


def move(shell: Any, args: Any, src: str, dest: str) -> None:
    src = shell.sabs_path(src)

    if shell.syscall.is_dir(src):
        srcpaths = shell.syscall.list_all(src)
    else:
        srcpaths = [src]

    if shell.syscall.is_dir(dest):
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
            if shell.syscall.is_dir(path):
                copy_dir(shell, path, destpath)
            else:
                shell.syscall.copy(path, destpath)
            copiedpaths.append(path)
        except OSError:
            shell.stderr.write("file error " + destpath)

    for path in reversed(copiedpaths):
        try:
            if shell.syscall.is_dir(path):
                shell.syscall.remove_dir(path)
            else:
                shell.syscall.remove(path)
        except OSError:
            shell.stderr.write("%s does not exist" % (path,))


def copy_dir(shell: Any, src: str, dest: str) -> None:
    shell.syscall.make_dir(dest)
    # TODO # add copy metedata to syscalls?
    meta = shell.syscall.get_meta_data(src)
    shell.syscall.set_owner(dest, meta[1])
    shell.syscall.set_permission(dest, meta[2])
    shell.syscall.set_time(dest, meta[3:6])


def help() -> str:
    return parser.help_msg()
