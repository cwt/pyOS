import hashlib
import getpass
from typing import Any, List, Dict


from kernel.constants import SystemState


def run(shell: Any, args: List[str]) -> None:
    # Check if we have automatic login credentials
    auto_user = getattr(shell.system, "_auto_login_user", None)
    auto_password = getattr(shell.system, "_auto_login_password", None)

    if auto_user and auto_password:
        # Use automatic login credentials
        user = auto_user
        password = hashlib.sha256(auto_password.encode()).hexdigest()
        # Clear the auto login credentials so they can't be reused
        delattr(shell.system, "_auto_login_user")
        delattr(shell.system, "_auto_login_password")
    else:
        # Prompt for credentials as usual
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
        # Use the existing system instance and set it to running state
        shell.system.state = SystemState.RUNNING
        # Create a new interpreter shell as a child of the current login shell
        newshell = shell.system.new_shell(
            parent=shell, path=path, program="interpreter"
        )
        add_vars(newshell, stuff)
        newshell.run()

        # If we reach here and we had automatic login, set system state to shutdown
        # to avoid returning to login prompt
        if auto_user and auto_password:
            shell.system.state = SystemState.SHUTDOWN
        # Note: We don't set the system state to SHUTDOWN here because the interpreter
        # shell should keep running until the user explicitly logs out
    else:
        shell.stderr.write("Invalid username or password.")
        shell.stderr.write("")


def add_vars(shell: Any, stuff: Dict[str, str]) -> None:
    for key in stuff:
        shell.set_var(key, stuff[key])


def help() -> str:
    a = """
    """
    return a
