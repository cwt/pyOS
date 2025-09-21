from typing import Optional, List, Tuple, Any, Union
import sqlite3
from contextlib import contextmanager

from kernel.utils import convert_many
from kernel.models import UserData


@contextmanager
def get_db_connection() -> Any:
    """Get a database connection with type detection."""
    from kernel.constants import USERDATAFILE

    con = sqlite3.connect(USERDATAFILE, detect_types=sqlite3.PARSE_DECLTYPES)
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def build_user_data_database() -> None:
    addsql = "INSERT INTO userdata VALUES (?, ?, ?, ?, ?, ?)"
    tablesql = """CREATE TABLE IF NOT EXISTS userdata (
                    username TEXT,
                    groupname TEXT,
                    info TEXT,
                    homedir TEXT,
                    shell TEXT,
                    password TEXT)"""

    root = (
        "root",
        "root",
        "Root",
        "/",
        "/programs/interpreter",
        "d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1",
    )  # pass
    chris = (
        "chris",
        "chris",
        "Chris",
        "/",
        "/programs/interpreter",
        "2744ccd10c7533bd736ad890f9dd5cab2adb27b07d500b9493f29cdc420cb2e0",
    )  # me
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute(tablesql)
        # Always insert the users - in tests, we start with a clean database
        cur.execute(addsql, root)
        cur.execute(addsql, chris)


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
            if result is not None:
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


def get_user_data(user: str) -> Optional[UserData]:
    data = execute_query(
        "SELECT username, groupname, info, homedir, shell, password FROM userdata WHERE username = ?",
        (user,),
        "one",
    )
    return UserData.from_tuple(data) if data else None  # type: ignore


def get_all_user_data() -> Optional[List[UserData]]:
    data = execute_query("SELECT * FROM userdata", (), "all")
    return [UserData.from_tuple(item) for item in data] if data else None  # type: ignore


#######################################


def add_user(
    user: str, group: str, info: str, homedir: str, shell: str, password: str
) -> None:
    addsql = "INSERT INTO userdata VALUES (?, ?, ?, ?, ?, ?)"

    execute_many(addsql, [(user, group, info, homedir, shell, password)])


def delete_user(user: str) -> None:
    user_converted = convert_many(user)
    delsql = "DELETE FROM userdata WHERE username = ?"

    execute_many(delsql, user_converted)


def change_user(user: str, value: Any) -> None:
    pass


#######################################


def get_group(user: str) -> str:
    data = get_user_data(user)
    if data:
        return data.groupname
    return ""


def get_info(user: str) -> str:
    data = get_user_data(user)
    if data:
        return data.info
    return ""


def get_homedir(user: str) -> str:
    data = get_user_data(user)
    if data:
        return data.homedir
    return ""


def get_shell(user: str) -> str:
    data = get_user_data(user)
    if data:
        return data.shell
    return ""


def set_group(user: str, value: str) -> None:
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute(
            "UPDATE userdata SET groupname = ? WHERE username = ?",
            (value, user),
        )


def set_info(user: str, value: str) -> None:
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute(
            "UPDATE userdata SET info = ? WHERE username = ?", (value, user)
        )


def set_homedir(user: str, value: str) -> None:
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute(
            "UPDATE userdata SET homedir = ? WHERE username = ?",
            (value, user),
        )


def set_shell(user: str, value: str) -> None:
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute(
            "UPDATE userdata SET shell = ? WHERE username = ?",
            (value, user),
        )


def set_password(user: str, value: str) -> None:
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute(
            "UPDATE userdata SET password = ? WHERE username = ?",
            (value, user),
        )


#######################################


def get_password(user: str) -> str:
    data = get_user_data(user)
    if data:
        return data.password
    return ""


def correct_password(user: str, password: str) -> bool:
    try:
        user_data = get_user_data(user)
        if user_data is None:
            return False
        return user_data.password == password
    except (TypeError, IndexError):
        return False
