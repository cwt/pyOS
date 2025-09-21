import os
import shutil
import glob
import importlib.util
from typing import List, Tuple, Any
from contextlib import contextmanager

from kernel.constants import BASEPATH
from kernel.exceptions import FileNotFoundError, DirectoryNotEmptyError


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


def split(path: str) -> Tuple[str, str]:
    return dir_name(path), base_name(path)


#######################################


def exists(path: str) -> bool:
    try:
        return os.path.exists(abs_path(path))
    except Exception:
        return False


def is_file(path: str) -> bool:
    try:
        return os.path.isfile(abs_path(path))
    except Exception:
        return False


def is_dir(path: str) -> bool:
    try:
        return os.path.isdir(abs_path(path))
    except Exception:
        return False


def copy(src: str, dst: str) -> None:
    try:
        shutil.copy2(abs_path(src), abs_path(dst))
    except IOError as e:
        raise FileNotFoundError(src, f"Failed to copy {src} to {dst}: {str(e)}")


def remove(path: str) -> None:
    try:
        os.remove(abs_path(path))
    except OSError as e:
        raise FileNotFoundError(path, f"Failed to remove {path}: {str(e)}")


def remove_dir(path: str) -> None:
    try:
        if list_dir(path) == []:
            shutil.rmtree(abs_path(path))
        else:
            raise DirectoryNotEmptyError(path)
    except OSError as e:
        raise DirectoryNotEmptyError(
            path, f"Failed to remove directory {path}: {str(e)}"
        )


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


@contextmanager
def open_file_context(path: str, mode: str) -> Any:
    """Context manager for file operations."""
    f = open(abs_path(path), mode)
    try:
        yield f
    finally:
        f.close()


def open_file(path: str, mode: str) -> Any:
    """Open a file and return a file object."""
    return open(abs_path(path), mode)


def open_program(path: str) -> Any:
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
