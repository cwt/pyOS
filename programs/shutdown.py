from kernel.system import System
from kernel.constants import SHUTDOWN
from typing import Any, List


def run(shell: Any, args: List[str]) -> None:
    System.state = SHUTDOWN


def help() -> str:
    a = """
    Shutdown

    Shuts down the OS.

    usage: shutdown
    """
    return a
