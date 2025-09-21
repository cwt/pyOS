from kernel.system import System
from kernel.constants import REBOOT
from typing import Any, List


def run(shell: Any, args: List[str]) -> None:
    System.state = REBOOT


def help() -> str:
    a = """
    Restart

    Restarts the OS.

    usage: restart
    """
    return a
