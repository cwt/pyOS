import re
import argparse
from typing import Any, List, Pattern

from kernel.utils import Parser
from kernel.common import resolve_path, handle_file_operation
from kernel.file_utils import read_file_lines

desc = "Search for lines in a file matching the pattern given."
parser = Parser("grep", name="Grep", description=desc)
pa = parser.add_argument
pa(
    "paths",
    type=str,
    nargs="*",
)
pa("-e", action="store", type=str, dest="pattern", default="")
pa("-a", action="store_true", dest="all", default=False)
pa("-i", action="store_true", dest="ignorecase", default=False)
pa("-v", action="store_true", dest="invert", default=False)


def run(shell: Any, args: List[str]) -> None:
    parser.add_shell(shell)
    parsed_args = parser.parse_args(args)
    if not parser.help:
        if parsed_args.paths:
            skip = 0
            # re.IGNORECASE is a number
            case = parsed_args.ignorecase * re.IGNORECASE
            if not parsed_args.pattern:
                pattern: Pattern[str] = re.compile(parsed_args.paths[0], case)
                skip = 1
            else:
                pattern = re.compile(parsed_args.pattern, case)

            for path in sorted(parsed_args.paths[skip:]):
                grep(shell, parsed_args, pattern, path)

            if shell.stdin:
                for line in shell.stdin.read():
                    # use xor to invert the selection
                    if bool(re.findall(pattern, line)) ^ parsed_args.invert:
                        shell.stdout.write(line.strip())
            if not shell.stdout:
                shell.stdout.write("")
        else:
            shell.stderr.write("missing file operand")


def grep(
    shell: Any, args: argparse.Namespace, pattern: Pattern[str], path: str
) -> None:
    newpath = resolve_path(shell, path)
    if handle_file_operation(shell, newpath, "is_file"):
        lines = read_file_lines(shell, newpath)
        for line in lines:
            # use xor to invert the selection
            if bool(re.findall(pattern, line)) ^ args.invert:
                if shell.stdout:
                    shell.stdout.write(line.rstrip())
                else:
                    shell.stdout.write("%s:%s" % (path, line.rstrip()))
    else:
        shell.stderr.write("%s does not exist" % (newpath,))


def help() -> str:
    return parser.help_msg()
