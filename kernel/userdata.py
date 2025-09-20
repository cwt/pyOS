from typing import Optional, List, Tuple, Any

from kernel.utils import convert_many
from kernel.metadata import get_db_connection, execute_query, execute_many


def build_user_data_database() -> None:
    addsql = "INSERT INTO userdata VALUES (?, ?, ?, ?, ?, ?)"
    tablesql = """CREATE TABLE IF NOT EXISTS userdata (
                    username TEXT,
                    groupname TEXT,
                    info TEXT,
                    homedir TEXT,
                    shell TEXT,
                    password TEXT)"""

    con = get_db_connection()
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
    with con:
        cur = con.cursor()
        cur.execute(tablesql)
        if get_user_data("chris") is None:
            cur.execute(addsql, chris)
        if get_user_data("root") is None:
            cur.execute(addsql, root)


def get_user_data(user: str) -> Optional[Tuple]:
    data = execute_query(
        "SELECT * FROM userdata WHERE username = ?", (user,), "one"
    )
    return data


def get_all_user_data() -> Optional[List[Tuple]]:
    data = execute_query("SELECT * FROM userdata", (), "all")
    return data


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
    return get_user_data(user)[1]


def set_group(user: str, value: str) -> None:
    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "UPDATE userdata SET groupname = ? WHERE username = ?",
            (value, user),
        )


def get_info(user: str) -> str:
    return get_user_data(user)[2]


def set_info(user: str, value: str) -> None:
    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "UPDATE userdata SET info = ? WHERE username = ?", (value, user)
        )


def get_homedir(user: str) -> str:
    return get_user_data(user)[3]


def set_homedir(user: str, value: str) -> None:
    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "UPDATE userdata SET homedir = ? WHERE username = ?", (value, user)
        )


def get_shell(user: str) -> str:
    return get_user_data(user)[4]


def set_shell(user: str, value: str) -> None:
    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "UPDATE userdata SET shell = ? WHERE username = ?", (value, user)
        )


def get_password(user: str) -> str:
    return get_user_data(user)[5]


def set_password(user: str, value: str) -> None:
    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "UPDATE userdata SET password = ? WHERE username = ?", (value, user)
        )


#######################################


def correct_password(user: str, password: str) -> bool:
    try:
        return get_password(user) == password
    except TypeError:
        return False
