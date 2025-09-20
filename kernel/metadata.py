import datetime
import sqlite3
from typing import Union, List, Tuple, Optional

from kernel.constants import METADATAFILE
from kernel.utils import calc_permission_number
from kernel.utils import convert_many


def get_db_connection():
    """Get a database connection with type detection."""
    return sqlite3.connect(METADATAFILE, detect_types=sqlite3.PARSE_DECLTYPES)


def execute_query(
    query: str, params: tuple = (), fetch: str = "all"
) -> Optional[Union[List[Tuple], Tuple]]:
    """Execute a database query with error handling."""
    con = get_db_connection()
    try:
        with con:
            cur = con.cursor()
            cur.execute(query, params)
            if fetch == "one":
                result = cur.fetchone()
            elif fetch == "all":
                result = cur.fetchall()
            else:
                result = None
            if result:
                # In Python 3, strings are already Unicode, so no conversion needed
                if isinstance(result, list):
                    result = [
                        tuple(
                            str(x) if isinstance(x, bytes) else x for x in row
                        )
                        for row in result
                    ]
                elif isinstance(result, tuple):
                    result = tuple(
                        str(x) if isinstance(x, bytes) else x for x in result
                    )
            return result
    except Exception:
        return None


def execute_many(query: str, params_list: List[tuple]) -> bool:
    """Execute a database query with multiple parameter sets."""
    con = get_db_connection()
    try:
        with con:
            cur = con.cursor()
            cur.executemany(query, params_list)
        return True
    except Exception:
        return False


def build_meta_data_database(fsmatches: List[str]) -> None:
    now = datetime.datetime.now()

    delsql = "DELETE FROM metadata WHERE path = ?"
    addsql = "INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)"
    tablesql = """CREATE TABLE IF NOT EXISTS metadata (
                    path TEXT,
                    owner TEXT,
                    permission TEXT,
                    created TIMESTAMP,
                    accessed TIMESTAMP,
                    modified TIMESTAMP)"""

    con = get_db_connection()
    try:
        with con:
            cur = con.cursor()
            cur.execute("SELECT path FROM metadata")
            fsmatches_set = set(fsmatches)
            dbmatches = set(x[0] for x in cur.fetchall())

            for x in fsmatches_set.difference(dbmatches):
                cur.execute(addsql, ((x, "root", "rwxrwxrwx", now, now, now)))
            for x in dbmatches.difference(fsmatches_set):
                cur.execute(delsql, (x,))

    except Exception:
        items = ((x, "root", "rwxrwxrwx", now, now, now) for x in fsmatches)

        with con:
            cur = con.cursor()
            cur.execute(tablesql)
            cur.executemany(addsql, items)


def get_meta_data(path: str) -> Optional[Tuple]:
    data = execute_query(
        "SELECT * FROM metadata WHERE path = ?", (path,), "one"
    )
    return data


def get_all_meta_data(path: str = "/") -> Optional[List[Tuple]]:
    data = execute_query(
        "SELECT * FROM metadata WHERE path LIKE ?", (path + "%",), "all"
    )
    return data


def add_path(path: str, owner: str, permission: str) -> None:
    now = datetime.datetime.now()

    validate_permission(permission)
    validate_owner(owner)

    data = convert_many(path, owner, permission, now, now, now)

    addsql = "INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)"

    execute_many(addsql, data)


def copy_path(src: str, dst: str) -> None:
    now = datetime.datetime.now()

    src_converted = convert_many(src)
    dst_converted = convert_many(dst)
    assert len(src_converted) == len(dst_converted)

    selsql = "SELECT owner,permission FROM metadata WHERE path = ?"
    addsql = "INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)"

    con = get_db_connection()
    with con:
        cur = con.cursor()
        temp = []
        for x in src_converted:
            cur.execute(selsql, x)
            temp.append(cur.fetchone())

        # fix for ignored files
        zipped = (
            (x, y) for (x, y) in zip(dst_converted, temp) if y is not None
        )
        data = [
            (path, owner, perm, now, now, now)
            for ((path,), (owner, perm)) in zipped
        ]
        cur.executemany(addsql, data)


def move_path(src: str, dst: str) -> None:
    now = datetime.datetime.now()

    src_converted = convert_many(src)
    dst_converted = convert_many(dst)
    assert len(src_converted) == len(dst_converted)

    data = [(x, now, y) for ((x,), (y,)) in zip(dst_converted, src_converted)]

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.executemany(
            "UPDATE metadata SET path = ?, modified = ? WHERE path = ?", data
        )


def delete_path(path: str) -> None:
    path_converted = convert_many(path)
    delsql = "DELETE FROM metadata WHERE path = ?"

    execute_many(delsql, path_converted)


def validate_permission(value: str) -> None:
    full = "rwxrwxrwx"
    assert len(value) == len(full)
    for perm_char, full_char in zip(value, full):
        assert (perm_char == "-") or (perm_char == full_char)


def get_permission_string(path: str) -> str:
    return get_meta_data(path)[2]


def get_permission_number(path: str) -> str:
    return calc_permission_number(get_meta_data(path)[2])


def set_permission_string(path: str, value: str) -> None:
    number = calc_permission_number(value)
    set_permission_number(path, number)


def set_permission_number(path: str, value: str) -> None:
    now = datetime.datetime.now()

    validate_permission(value)

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "UPDATE metadata SET permission = ?, modified = ? WHERE path = ?",
            (value, now, path),
        )


def set_permission(path: str, value: Union[str, int]) -> None:
    try:
        set_permission_number(path, int(value))
    except ValueError:
        set_permission_string(path, str(value))


def set_time(
    path: str, value: Optional[Union[dict, str, tuple, list]] = None
) -> None:
    if isinstance(value, dict):
        set_time_dict(path, value)
    elif isinstance(value, str):
        set_time_string(path, value)
    elif isinstance(value, (tuple, list)):
        set_time_list(path, value)
    else:
        raise TypeError


def set_time_list(path: str, value: Union[tuple, list]) -> None:
    con = get_db_connection()
    columns = ["accessed", "created", "modified"]

    a = [x + " = ?" for (x, y) in zip(columns, value) if y is not None]
    b = tuple(x for x in value if x is not None)
    upsql = "UPDATE metadata SET %s WHERE path = ?" % ", ".join(a)

    with con:
        cur = con.cursor()
        cur.execute(upsql, b + (path,))


def set_time_dict(path: str, value: Optional[dict] = None) -> None:
    done = [None, None, None]
    d = {
        "a": 0,
        "access": 0,
        "accessed": 0,
        "m": 1,
        "modify": 1,
        "modified": 1,
        "c": 2,
        "create": 2,
        "created": 2,
    }
    if value:
        for key in value:
            done[d[key]] = value[key]
    set_time_list(path, done)


def set_time_string(path: str, value: Optional[str] = None) -> None:
    # some magic that should not exist
    done = [None, None, None]
    d = {"a": 0, "c": 1, "m": 2}
    timeinc = {
        "w": "weeks",
        "d": "days",
        "h": "hours",
        "m": "minutes",
        "s": "seconds",
    }

    if value:
        for time in value.split(","):
            time = time.strip()
            if time:
                lvl = time[0]
                try:
                    other = float(time[1:-1])
                except ValueError:
                    other = 0.0
                if len(time) >= 2:
                    unit = time[-1]
                else:
                    unit = "n"

                if unit == "y":
                    unit = "d"
                    other *= 365  # year is not defined, assuming 365 days
                elif unit == "n":
                    unit = "d"
                    other = 0.0
                delta = datetime.timedelta(**{timeinc[unit]: other})
                if done[d[lvl]] is None:
                    done[d[lvl]] = delta
                else:
                    done[d[lvl]] += delta

    done = [
        x + datetime.datetime.now() if x is not None else None for x in done
    ]
    set_time_list(path, done)


def get_time(path: str) -> Tuple:
    return get_meta_data(path)[3:6]


def get_owner(path: str) -> str:
    return get_meta_data(path)[1]


def validate_owner(owner: str) -> str:
    # TODO # validate owner
    return owner


def set_owner(path: str, owner: str) -> None:
    now = datetime.datetime.now()

    value = validate_owner(owner)

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "UPDATE metadata SET owner = ?, modified = ? WHERE path = ?",
            (value, path, now),
        )
