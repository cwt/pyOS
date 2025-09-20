import os
import shutil
import glob
import importlib.util
from typing import List

from kernel.constants import BASEPATH


def abs_path(path: str) -> str:
    # returns external absolute path
    return os.path.abspath(os.path.join(BASEPATH, path.lstrip("/")))


def rel_path(path: str, base: str) -> str:
    # returns external relative path
    return os.path.relpath(path, base)


def irel_path(path: str) -> str:
    # returns internal relative path
    b = os.path.relpath(path, BASEPATH)
    b = b.replace("../", "")
    if b in ("..", "."):
        b = ""
    return b


def iabs_path(path: str) -> str:
    # returns internal absolute path
    b = os.path.relpath(path, BASEPATH)
    c = irel_path(b)
    return join_path("/", c)


def join_path(*args: str) -> str:
    return os.path.join(*args)


def dir_name(path: str) -> str:
    return os.path.dirname(path)


def base_name(path: str) -> str:
    return os.path.basename(path)


def split(path: str) -> tuple[str, str]:
    return dir_name(path), base_name(path)


#######################################


def exists(path: str) -> bool:
    return os.path.exists(abs_path(path))


def is_file(path: str) -> bool:
    return os.path.isfile(abs_path(path))


def is_dir(path: str) -> bool:
    return os.path.isdir(abs_path(path))


def copy(src: str, dst: str) -> None:
    shutil.copy2(abs_path(src), abs_path(dst))


def remove(path: str) -> None:
    os.remove(abs_path(path))


def remove_dir(path: str) -> None:
    if list_dir(path) == []:
        shutil.rmtree(abs_path(path))
    else:
        raise OSError


def get_size(path: str) -> int:
    return os.path.getsize(abs_path(path))


def list_dir(path: str) -> List[str]:
    return sorted(
        x
        for x in os.listdir(abs_path(path))
        if ".git" not in x and not x.endswith(".pyc")
    )


def list_glob(expression: str) -> List[str]:
    return [iabs_path(x) for x in glob.glob(abs_path(expression))]


def list_all(path: str = "/") -> List[str]:
    listing = [path]
    for x in list_dir(path):
        new = join_path(path, x)
        if is_dir(new):
            listing.extend(list_all(new))
        else:
            listing.append(new)
    return listing


def make_dir(path: str) -> None:
    os.mkdir(abs_path(path))


def open_file(path: str, mode: str):
    return open(abs_path(path), mode)


def open_program(path: str):
    x = abs_path(path)
    if not is_dir(path):
        try:
            spec = importlib.util.spec_from_file_location("program", x)
            if spec and spec.loader:
                program = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(program)
            else:
                program = False
        except (IOError, FileNotFoundError):
            program = False
    else:
        program = False
    return program
