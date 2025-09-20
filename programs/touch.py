import datetime
from typing import Any, List, Optional

from kernel.utils import Parser


desc = "Creates an empty file at the given path."
parser = Parser("touch", name="Touch", description=desc)
pa = parser.add_argument
pa("paths", type=str, nargs="*")

pa("-c", action="store_true", dest="created", default=False)
pa("-a", action="store_true", dest="accessed", default=False)
pa("-m", action="store_true", dest="modified", default=False)

pa("-d", action="store", type=str, dest="date", default=None)
pa("-t", action="store", type=str, dest="timestamp", default=None)


def run(shell: Any, args: List[str]) -> None:
    parser.add_shell(shell)
    args = parser.parse_args(args)
    if not parser.help:
        timestuff = any([args.date, args.timestamp])
        if args.paths:
            if args.date and args.timestamp:
                shell.stderr.write(
                    "cannot specify times from more than one source"
                )
            else:
                times = get_times(args)
                for x in args.paths:
                    path = shell.sabs_path(x)
                    if not shell.syscall.is_dir(path):
                        shell.syscall.open_file(path, "a").close()
                    if timestuff:
                        shell.syscall.set_time(path, times)
        else:
            shell.stderr.write("missing file operand")


def get_times(args: Any) -> List[Optional[datetime.datetime]]:
    time = None
    types = [args.accessed, args.created, args.modified]
    if args.date is not None:
        time = parse_date(args.date)
    elif args.timestamp is not None:
        time = parse_time_stamp(args.timestamp)
    if not any(types):
        done = [time] * 3
    else:
        done = [time if x else None for x in types]
    return done


def parse_time_stamp(time: str) -> Optional[datetime.datetime]:
    a = datetime.datetime.now()
    done = None
    format_str = "%m%d%H%M%S"
    if "." in time:
        format_str += ".%f"

    try:
        done = datetime.datetime.strptime(time, format_str).replace(year=a.year)
    except Exception:
        try:
            done = datetime.datetime.strptime(time, "%y" + format_str)
        except Exception:
            done = datetime.datetime.strptime(time, "%Y" + format_str)
    return done


def parse_date(time: str) -> Optional[datetime.datetime]:
    a = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    ltime = len(time)
    done = None
    if 1 <= ltime <= 2:
        # hours
        done = a.replace(hour=int(time))
    elif 3 <= ltime <= 4:
        # hours minutes
        hour = int(time[0:2])
        minute = int(time[2:])
        done = a.replace(hour=hour, minute=minute)
    elif 5 <= ltime <= 6:
        # year month day
        day = int(time[4:])
        month = int(time[2:4])
        if int(time[0:2]) < 69:
            year = 2000 + int(time[0:2])
        else:
            year = 1900 + int(time[0:2])
        done = a.replace(year=year, month=month, day=day)
    elif 7 <= ltime:
        # year month day
        day = int(time[-2:])
        month = int(time[-4:-2])
        year = int(time[:-4])
        done = a.replace(year=year, month=month, day=day)
    return done


def help() -> str:
    return parser.help_msg()
