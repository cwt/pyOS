import re
import fnmatch
import datetime
import argparse
from typing import Any, List, Optional, Dict

from kernel.utils import Parser

desc = "Finds files matching the expression given."
parser = Parser("find", name="Find", description=desc)
pa = parser.add_argument
pa(
    "paths",
    type=str,
    nargs="*",
)

pa("-time", action="store", type=str, nargs="*", dest="time", default=None)
pa("-newer", action="store", type=str, nargs="*", dest="newer", default=None)

pa("-perm", action="store", type=str, nargs="*", dest="perm", default=None)
pa("-readable", action="store_true", dest="readable", default=False)
pa("-writable", action="store_true", dest="writable", default=False)
pa("-executable", action="store_true", dest="executable", default=False)

pa("-exp", action="store", type=str, dest="expression", default=None)

pa("-depth", action="store_true", dest="depth", default=False)
pa("-maxdepth", action="store", type=int, dest="maxdepth", default=None)
pa("-mindepth", action="store", type=int, dest="mindepth", default=None)

pa("-empty", action="store_true", dest="empty", default=False)

pa("-uid", action="store", type=int, nargs="*", dest="uid", default=None)
pa("-user", action="store", type=str, nargs="*", dest="user", default=None)
pa("-nouser", action="store_true", dest="nouser", default=False)

pa("-gid", action="store", type=int, nargs="*", dest="gid", default=None)
pa("-group", action="store", type=str, nargs="*", dest="group", default=None)
pa("-nogroup", action="store_true", dest="nogroup", default=False)

# -empty
# -false
# -true

# -fstype TYPE
# -ilname PATTERN
# -iname PATTERN
# -inum N
# -iwholename PATTERN
# -iregex PATTERN
# -links N
# -lname PATTERN
# -wholename PATTERN
# -path PATTERN
# -regex PATTERN

# -size N[bcwkMG]
# -used N
# -type [bcdpflsD]
# -xtype [bcdpfls]


def run(shell: Any, args: List[str]) -> None:
    parser.add_shell(shell)
    parsed_args = parser.parse_args(args)
    if not parser.help:
        if parsed_args.paths:
            paths = parsed_args.paths
        else:
            paths = ["/"]
        now = datetime.datetime.now()
        perms = convert_permissions(shell, parsed_args)
        times = convert_time(parsed_args, now)
        for path in paths:
            a = find(shell, parsed_args, shell.sabs_path(path), perms, times)
            for x in a:
                shell.stdout.write(x)
        if not shell.stdout:
            shell.stdout.write("")


def find(
    shell: Any,
    args: argparse.Namespace,
    basepath: str,
    perms: Optional[str],
    times: Dict[str, List[Optional[datetime.datetime]]],
) -> List[str]:
    done = []
    access, modify, create = times
    get_data = shell.syscall.get_all_meta_data
    for path, uid, perm, created, accessed, modified in get_data(basepath):
        mtimes = {"a": accessed, "m": modified, "c": created}
        plen = len([x for x in path.split("/") if x])
        if args.expression:
            if not fnmatch.fnmatchcase(path, args.expression):
                continue
        if args.mindepth is not None:
            if args.mindepth > plen:
                continue
        if args.maxdepth is not None:
            if plen > args.maxdepth:
                continue
        out = False
        for key in times:
            (newest, oldest) = times[key]
            if oldest is not None:
                if mtimes[key] < oldest:
                    out = True
                    continue
            if newest is not None:
                if newest < mtimes[key]:
                    out = True
                    continue
        if out:
            continue
        if perms is not None:
            if not re.findall(perms, perm):
                continue
        done.append(path)
    return done


def convert_time(
    args: argparse.Namespace, now: datetime.datetime
) -> Dict[str, List[Optional[datetime.datetime]]]:
    d: Dict[str, List[Optional[datetime.timedelta]]] = {
        "a": [None, None],
        "m": [None, None],
        "c": [None, None],
    }

    timeinc = {
        "w": "weeks",
        "d": "days",
        "h": "hours",
        "m": "minutes",
        "s": "seconds",
    }

    # this is used to fix leap years
    year = 365.2425
    if args.time:
        for time in args.time:
            lvl = time[0]
            op = time[1]
            other = float(time[2:-1])
            unit = time[-1]

            if unit == "y":
                unit = "d"
                other *= year
            t = datetime.timedelta(**{timeinc[unit]: other})

            if op == "+":
                if d[lvl][0] is None or (t is not None and d[lvl][0] is not None and t > d[lvl][0]):  # type: ignore
                    d[lvl][0] = t
            elif op == "-":
                if d[lvl][1] is None or (t is not None and d[lvl][1] is not None and t < d[lvl][1]):  # type: ignore
                    d[lvl][1] = t
    result: Dict[str, List[Optional[datetime.datetime]]] = {}
    for key in d:
        result[key] = [(now - x) if x is not None else None for x in d[key]]
    return result


def convert_permissions(shell: Any, args: argparse.Namespace) -> Optional[str]:
    d = {"u": list("..."), "g": list("..."), "o": list("...")}
    perm_result: Optional[str] = None
    if args.perm is not None:
        try:
            int(args.perm[0])
            perm_result = shell.syscall.calc_permission_string(args.perm[0])
        except Exception:
            for permset in ",".join(args.perm).split(","):
                lvl = permset[0]
                op = permset[1]
                perm = permset[2:]

                if op == "=":
                    d[lvl] = [
                        x if perm is not None and x in perm else "-"
                        for x in "rwx"
                    ]
                elif op == "-":
                    d[lvl] = [
                        "-" if perm is not None and x in perm else d[lvl][i]
                        for i, x in enumerate("rwx")
                    ]
                elif op == "+":
                    d[lvl] = [
                        x if perm is not None and x in perm else d[lvl][i]
                        for i, x in enumerate("rwx")
                    ]
            perm_result = "".join(["".join(d[key]) for key in "ugo"])

    return perm_result


def help() -> str:
    return parser.help_msg()
