import datetime
import sqlite3
from typing import Union, List, Tuple, Optional, Any, Dict
from contextlib import contextmanager

from kernel.constants import METADATAFILE
from kernel.utils import calc_permission_number, calc_permission_string
from kernel.utils import convert_many
from kernel.models import FileMetadata


# Register adapters and converters for datetime objects to avoid DeprecationWarning in Python 3.12+
def adapt_datetime(val: datetime.datetime) -> str:
    """Convert datetime to string for SQLite storage."""
    return val.isoformat()


def convert_datetime(val: bytes) -> datetime.datetime:
    """Convert string from SQLite to datetime object."""
    return datetime.datetime.fromisoformat(val.decode())


# Register the adapters and converters
sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)
sqlite3.register_converter("TIMESTAMP", convert_datetime)


@contextmanager
def get_db_connection() -> Any:
    """Context manager for database connections."""
    con = sqlite3.connect(METADATAFILE, detect_types=sqlite3.PARSE_DECLTYPES)
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def execute_query(
    query: str, params: Tuple[Any, ...] = (), fetch: str = "all"
) -> Optional[Union[List[Tuple[Any, ...]], Tuple[Any, ...]]]:
    """Execute a database query with error handling."""
    try:
        with get_db_connection() as con:
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
            # Type cast to satisfy mypy
            return result  # type: ignore
    except Exception:
        return None


def execute_many(query: str, params_list: List[Tuple[Any, ...]]) -> bool:
    """Execute a database query with multiple parameter sets."""
    try:
        with get_db_connection() as con:
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

    try:
        with get_db_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT path FROM metadata")
            fsmatches_set = set(fsmatches)
            dbmatches = set(x[0] for x in cur.fetchall())

            for x in fsmatches_set.difference(dbmatches):
                cur.execute(addsql, ((x, "root", "rwxrwxrwx", now, now, now)))
            for x in dbmatches.difference(fsmatches_set):
                cur.execute(delsql, (x,))
    except Exception:
        with get_db_connection() as con2:
            try:
                items = (
                    (x, "root", "rwxrwxrwx", now, now, now) for x in fsmatches
                )
                cur = con2.cursor()
                cur.execute(tablesql)
                cur.executemany(addsql, items)
            except Exception:
                pass


def get_meta_data(path: str) -> Optional[FileMetadata]:
    data = execute_query(
        "SELECT * FROM metadata WHERE path = ?", (path,), "one"
    )
    return FileMetadata.from_tuple(data) if data else None  # type: ignore


def get_all_meta_data(path: str = "/") -> Optional[List[FileMetadata]]:
    data = execute_query(
        "SELECT * FROM metadata WHERE path LIKE ?", (path + "%",), "all"
    )
    return [FileMetadata.from_tuple(item) for item in data] if data else None  # type: ignore


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

    with get_db_connection() as con:
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

    with get_db_connection() as con:
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
    data = get_meta_data(path)
    if data:
        return data.permission
    return ""


def get_permission_number(path: str) -> str:
    data = get_meta_data(path)
    if data:
        return calc_permission_number(data.permission)
    return ""


def set_permission_string(path: str, value: str) -> None:
    validate_permission(value)
    now = datetime.datetime.now()

    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute(
            "UPDATE metadata SET permission = ?, modified = ? WHERE path = ?",
            (value, now, path),
        )


def set_permission_number(path: str, value: str) -> None:
    # Convert number to string permission format
    permission_string = calc_permission_string(value)
    set_permission_string(path, permission_string)


def set_permission(path: str, value: Union[str, int]) -> None:
    try:
        set_permission_number(path, str(int(value)))
    except ValueError:
        set_permission_string(path, str(value))


def set_time(
    path: str,
    value: Optional[
        Union[Dict[str, Any], str, Tuple[Any, ...], List[Any]]
    ] = None,
) -> None:
    if isinstance(value, dict):
        set_time_dict(path, value)
    elif isinstance(value, str):
        set_time_string(path, value)
    elif isinstance(value, (tuple, list)):
        set_time_list(path, value)
    else:
        raise TypeError


def set_time_list(path: str, value: Union[Tuple[Any, ...], List[Any]]) -> None:
    columns = ["accessed", "created", "modified"]

    a = [x + " = ?" for (x, y) in zip(columns, value) if y is not None]
    b = tuple(x for x in value if x is not None)
    upsql = "UPDATE metadata SET %s WHERE path = ?" % ", ".join(a)

    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute(upsql, b + (path,))


def set_time_dict(path: str, value: Optional[Dict[str, Any]] = None) -> None:
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

                unit = "d"
                other = 0.0
            delta = datetime.timedelta(**{timeinc[unit]: other})
            if done[d[lvl]] is None:
                done[d[lvl]] = delta
            else:
                # Create a new list with the updated value to avoid the typing issue
                current_value = done[d[lvl]]
                if current_value is not None:
                    done[d[lvl]] = current_value + delta  # type: ignore

    done = [
        x + datetime.datetime.now() if x is not None else None for x in done
    ]
    set_time_list(path, done)


def get_time(path: str) -> Tuple[Any, ...]:
    data = get_meta_data(path)
    if data:
        return (data.created, data.accessed, data.modified)
    return ()


def get_owner(path: str) -> str:
    data = get_meta_data(path)
    if data:
        return data.owner
    return ""


def validate_owner(owner: str) -> str:
    # TODO # validate owner
    return owner


def set_owner(path: str, owner: str) -> None:
    now = datetime.datetime.now()

    value = validate_owner(owner)

    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute(
            "UPDATE metadata SET owner = ?, modified = ? WHERE path = ?",
            (value, now, path),
        )
