import time
import random
from typing import Any, List


def run(shell: Any, args: List[str]) -> None:
    for x in range(20):
        shell.stdout.write(str(x))
        time.sleep(1 * random.random())


def help() -> str:
    return ""
