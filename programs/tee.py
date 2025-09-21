from typing import Any, List
from kernel.utils import Parser


desc = "Allows tapping into the stdout to write to multiple files."
parser = Parser("tee", name="Tee", description=desc)
pa = parser.add_argument
pa(
    "paths",
    type=str,
    nargs="*",
)
pa("-a", action="store_true", dest="append", default=False)


def run(shell: Any, args: List[str]) -> None:
    parser.add_shell(shell)
    parsed_args = parser.parse_args(args)
    if not parser.help:
        if parsed_args.paths:
            if parsed_args.append:
                mode = "a"
            else:
                mode = "w"
            if parsed_args.paths:
                files = []
                for x in parsed_args.paths:
                    try:
                        files.append(shell.syscall.open_file(x, mode))
                    except Exception:
                        pass
                for line in shell.stdin.read():
                    for f in files:
                        f.write(line)
                    shell.stdout.write(line)
                for f in files:
                    f.close()
        else:
            for line in shell.stdin.read():
                print(line)
                shell.stdout.write(line)


def help() -> str:
    return parser.help_msg()
