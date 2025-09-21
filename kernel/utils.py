import argparse
from typing import Union, List, Tuple, Any, Optional


class Parser(argparse.ArgumentParser):
    def __init__(
        self,
        program: str,
        name: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Remove prog from kwargs if it exists to avoid duplicate keyword argument
        kwargs.pop("prog", None)
        argparse.ArgumentParser.__init__(self, prog=program, *args, **kwargs)  # type: ignore[misc]
        if name is None:
            self.name = program
        else:
            self.name = name
        self.help = False

    def add_shell(self, shell: Any) -> None:
        self.shell = shell

    def exit(self, *args: Any, **kwargs: Any) -> None:  # type: ignore
        pass

    def print_usage(self, *args: Any, **kwargs: Any) -> None:
        try:
            self.shell.stderr.write(self.format_usage())
            self.help = True
        except AttributeError:
            pass

    def print_help(self, *args: Any, **kwargs: Any) -> None:
        try:
            self.shell.stdout.write(self.help_msg())
            self.help = True
        except AttributeError:
            pass

    def help_msg(self) -> str:
        return "%s\n\n%s" % (self.name, self.format_help())


def calc_permission_string(number: Union[str, int]) -> str:
    base = "rwxrwxrwx"
    number_str = str(number)
    binary = []
    for digit in number_str[:3]:
        binary.extend([int(y) for y in "{0:03b}".format(int(digit))])
    return "".join([b if (a and b) else "-" for a, b in zip(binary, base)])


def calc_permission_number(string: str) -> str:
    numbers = []
    string_padded = string + "-" * (9 - len(string))
    for group in (string_padded[:3], string_padded[3:6], string_padded[6:9]):
        a = ["1" if x and x not in ["-", "0"] else "0" for x in group]
        numbers.append(int("0b" + "".join(a), 2))
    return "".join((str(x) for x in numbers))


def validate_permission(value: str) -> None:
    full = "rwxrwxrwx"
    assert len(value) == len(full)
    for perm_char, full_char in zip(value, full):
        assert (perm_char == "-") or (perm_char == full_char)


def check_permission(permissions: str, category: str, permission: str) -> bool:
    """Check if a specific permission is set for a category (user, group, other).

    Args:
        permissions: Permission string like "rwxrwxrwx"
        category: Category to check ('u' for user, 'g' for group, 'o' for other)
        permission: Permission to check ('r', 'w', or 'x')

    Returns:
        True if the permission is set, False otherwise
    """
    # Define the mapping of categories to their positions in the permission string
    category_positions = {
        "u": (0, 3),  # user: positions 0-2
        "g": (3, 6),  # group: positions 3-5
        "o": (6, 9),  # other: positions 6-8
    }

    # Define the mapping of permissions to their positions within a category
    permission_positions = {
        "r": 0,  # read: first position in category
        "w": 1,  # write: second position in category
        "x": 2,  # execute: third position in category
    }

    # Get the position range for the category
    if category not in category_positions:
        return False

    start_pos, end_pos = category_positions[category]

    # Get the position within the category
    if permission not in permission_positions:
        return False

    pos_in_category = permission_positions[permission]

    # Check if the permission is set
    return permissions[start_pos + pos_in_category] == permission


def convert_many(
    start: Union[List[str], Tuple[str, ...], str], *args: Any
) -> List[Tuple[str, ...]]:
    if not isinstance(start, (list, set, tuple)):
        done = [(start,) + args]
    else:
        done = [(x,) + args for x in start]
    return done
