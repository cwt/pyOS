import hashlib
import getpass
from typing import Any, List


from kernel.system import System


def run(shell: Any, args: List[str]) -> None:
    try:
        user = input("user: ")
    except (EOFError, KeyboardInterrupt):
        return
    try:
        password = hashlib.sha256(
            getpass.getpass("password: ").encode()
        ).hexdigest()
    except (EOFError, KeyboardInterrupt):
        return

    if shell.syscall.correct_password(user, password):  # == db(user).password
        stuff = {
            "USER": user,
            "SHELL": "interpreter",
            "USERNAME": user,
            "HOME": "/",  # db(user).homedir
        }

        path = "/"  # db(user).homedir
        newshell = System.new_shell(parent=shell, path=path)
        add_vars(newshell, stuff)
        newshell.run()
    else:
        shell.stderr.write("Invalid username or password.")
        shell.stderr.write("")


def add_vars(shell: Any, stuff: dict) -> None:
    for key in stuff:
        shell.set_var(key, stuff[key])


def help() -> str:
    a = """
    """
    return a
