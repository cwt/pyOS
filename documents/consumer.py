import time
import random
from typing import Any, List


def run(shell: Any, args: List[str]) -> None:
    for line in shell.stdin.read():
        print(line)
        time.sleep(1 * random.random())


def help() -> str:
    return ""
