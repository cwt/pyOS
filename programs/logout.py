from kernel.constants import IDLE
from typing import Any, List


def run(shell: Any, args: List[str]) -> None:
    # Set the system state to IDLE to return to the login prompt
    shell.system.state = IDLE


def help() -> str:
    a = """
    Logout

    Logs out the current user and returns to the login prompt.

    usage: logout
    """
    return a
