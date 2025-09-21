from typing import Any, List
from kernel.utils import Parser
from kernel.common import resolve_path
from kernel.file_utils import read_file_lines

desc = "Returns the first n lines of a file."
parser = Parser("head", name="Head", description=desc)
pa = parser.add_argument
pa(
    "paths",
    type=str,
    nargs="*",
)
pa("-n", action="store", type=int, dest="lineamount", default=5)


def run(shell: Any, args: List[str]) -> None:
    parser.add_shell(shell)
    parsed_args = parser.parse_args(args)
    if not parser.help:
        for x in parsed_args.paths:
            path = resolve_path(shell, x)
            if len(parsed_args.paths) > 1 or shell.stdin:
                shell.stdout.write("==> %s <==" % (x,))
            lines = read_file_lines(shell, path)
            for line in lines[: parsed_args.lineamount]:
                shell.stdout.write(line.rstrip())
        if shell.stdin:
            if parsed_args.paths:
                shell.stdout.write("==> %% stdin %% <==")
            stdin_lines = []
            try:
                stdin_lines = list(shell.stdin.read())
            except Exception:
                pass
            for line in stdin_lines[: parsed_args.lineamount]:
                shell.stdout.write(line)
            shell.stdout.write("")
        else:
            if not parsed_args.paths:
                shell.stderr.write("missing file operand")


def help() -> str:
    return parser.help_msg()
