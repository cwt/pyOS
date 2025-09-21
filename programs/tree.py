from typing import Any, List, Union


def run(shell: Any, args: List[str]) -> None:
    if args:
        path = shell.sabs_path(args[0])
    else:
        path = shell.path
    tree = tree_gen(path, shell.syscall)
    shell.stdout.write(tree_print(tree, shell.syscall))


def sorter(x: str, fs: Any) -> str:
    return ("f" if fs.is_file(x) else "d") + x.lower()


def tree_gen(path: str, fs: Any) -> List[Union[str, List[Any]]]:
    pathtree: List[Union[str, List[Any]]] = [path]
    if fs.is_dir(path):
        listing = sorted(
            [fs.join_path(path, x) for x in fs.list_dir(path)],
            key=lambda x: sorter(x, fs),
        )
        for x in listing:
            pathtree.append(tree_gen(fs.join_path(path, x), fs))
    return pathtree


def tree_print(
    tree: List[Union[str, List[Any]]],
    fs: Any,
    level: int = 0,
    extra: str = "",
    idx: bool = None,
) -> str:
    string = ""
    for i, x in enumerate(tree):
        spacing = "   " if (level > 1) else ""
        bar = "|" if (level > 0) else ""
        added = extra + spacing + bar
        if type(x) is list:
            string += tree_print(x, fs, level + 1, added, len(tree) - 1 == i)
        else:
            char = "-- " if fs.is_file(x) else "++ "
            if x != "/":
                x = fs.base_name(x)
            end = "%s%s\n" % (char if (level > 0) else "", x)
            if not idx:
                string += "%s%s" % (added, end)
            else:
                string += "%s`%s" % (added[:-1], end)
    return string


def help() -> str:
    a = """
    Tree

    Returns the file/directory tree of the given directory.

    usage: tree [directory]
    """
    return a
