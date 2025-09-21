import re
import argparse
from typing import Any, List, Tuple, Union

from kernel.utils import Parser

desc = "Allows editing streams."
parser = Parser("sed", name="Stream Editor", description=desc)
pa = parser.add_argument
pa(
    "paths",
    type=str,
    nargs="*",
)
pa("-e", action="append", type=str, dest="expression")
pa("-f", action="store", type=str, nargs="*", dest="file", default="")
pa("-s", action="store_true", dest="separate", default=False)
pa("-v", action="store_true", dest="invert", default=False)
pa("-i", action="store_true", dest="inplace", default=False)
pa("-n", action="store_true", dest="silent", default=False)


subparse = re.compile(r"""(s)(?P<lim>.)(.*?)(?P=lim)(.*?)(?P=lim)(.*)""")


def run(shell: Any, args: List[str]) -> None:
    parser.add_shell(shell)
    parsed_args = parser.parse_args(args)
    if not parser.help:
        if parsed_args.paths:
            for path in parsed_args.paths:
                sed(shell, parsed_args, path)
            if not shell.stdout:
                shell.stdout.write("")
        else:
            shell.stderr.write("no stream")


def sed(shell: Any, args: argparse.Namespace, path: str) -> None:
    newpath = shell.sabs_path(path)
    if shell.syscall.is_file(newpath):
        if args.inplace:
            out = shell.syscall.open_file(newpath + "~", "w")
        else:
            out = shell.stdout
        # iterator to find length of file
        with shell.syscall.open_file(newpath, "r") as f:
            for lenfile, x in enumerate(f):
                pass
        with shell.syscall.open_file(newpath, "r") as f:
            try:
                address, command = parse_expression(args.expression[0])

                singleregex = (address[0] == address[-1]) and (
                    isinstance(address[-1], str)
                )
                address = [lenfile if x == "$" else x for x in address]
                if (
                    len(address) > 0
                    and isinstance(address[-1], str)
                    and address[-1].startswith("+")
                ):
                    address[-1] = address[0] + int(address[-1][1:])  # type: ignore
                if all(isinstance(x, int) for x in address):
                    address[-1] = max(address)
                start = False
                end = False
                linematch = False
                for i, line in enumerate(f):
                    if match(i, line, address[0]) and not start:
                        start = True
                    if (start and not end) != command.startswith("!"):
                        line = edit_line(line, command)
                        linematch = True
                    if not args.inplace:
                        line = line.rstrip("\n")
                    if not linematch and args.silent:
                        pass
                    else:
                        out.write(line)
                    if match(i, line, address[-1]) and not end:
                        end = True

                    # do resets
                    linematch = False
                    if singleregex:
                        start = False
                        end = False

                if args.inplace:
                    out.close()
                    # TODO # replace
                    shell.syscall.copy(newpath + "~", newpath)
                    shell.syscall.remove(newpath + "~")
            except Exception:
                shell.stderr.write("No command")
    else:
        shell.stderr.write("%s does not exist" % (newpath,))


def match(i: int, line: str, address: Union[int, str]) -> bool:
    if isinstance(address, int):
        val = i >= address
    else:
        val = bool(re.findall(address, line))
    return val


def edit_line(line: str, expression: str) -> str:
    try:
        command, sep, regex, repl, flags = re.findall(subparse, expression)[0]
        if command == "s":
            newline = ""
            idx = 0
            for m in re.finditer(regex, line):
                r = repl.replace("&", m.group(0))
                newline += line[idx : m.start()] + r
                idx = m.end()
            newline += line[idx:]
        else:
            newline = line
    except Exception:
        newline = line
    return newline


def parse_expression(expression: str) -> Tuple[List[Union[int, str]], str]:
    commands = "qdpnsy!"
    split = re.split("""((?<!\\\\)/.*(?<!\\\\)/)""", expression)
    idx = None
    # separate the groupings
    for i, group in enumerate(split):
        if not group.startswith("/") and any(x in group for x in commands):
            idx = i
            break

    addrstr = "".join(split[:idx])
    cmdstr = ""
    end = 0
    # separate the individual chars
    for letter in "".join(split[idx:]):
        if not end:
            if letter not in commands:
                addrstr += letter
            else:
                end = 1
                cmdstr += letter
        else:
            cmdstr += letter

    address: List[Union[int, str]] = addrstr.split(",")
    # clean address values
    for i, value in enumerate(address):
        if isinstance(value, str) and not value.startswith("+"):
            try:
                address[i] = int(value) - 1
            except Exception:
                # remove the slashes
                if (
                    isinstance(value, str)
                    and value.startswith("/")
                    and value.endswith("/")
                ):
                    address[i] = value[1:-1]
    command = cmdstr
    return address, command


def help() -> str:
    return parser.help_msg()


# http://www.gnu.org/software/sed/manual/sed.html
# http://www.ibm.com/developerworks/linux/library/l-sed1/index.html
# Address ranges
# ==============
# first part of line
# [start,end]
# /regex/command
# /[beginregex]/,/[endregex]/command
# !
# \d*(?<,)\d*


# Commands
# ========
# #comment
# q [exit code]       quit at end of pattern space
# d                   delete the pattern space
# p                   print out pattern
# n                   print pattern space and insert next line
# { commands }        group of commands
# s                   s/regex/replacement/flags
#     replacement
#         \L          turn replacement lowercase until \U or \E
#         \l          turn the next char lowercase
#         \U          turn replacement uppercase until \L or \E
#         \u          turn the next char to uppercase
#         \E          Stop case conversion
#         \[n]        number of inclusions
#         &           matched pattern
#     flags
#         g           apply replacement to all matches
#         [num]       only replace the /num/th match
#         p           if sub was made, print pattern space
#         w [file]    if sub was made, write result to file
#                     this incudes /dev/stdout/ and /dev/stderr/
#         i/I         case insensitive match
#         m/M         multiline?
# y                   /source-chars/dest-chars/
