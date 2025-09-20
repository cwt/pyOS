import argparse
from typing import Union, List, Tuple, Any


class Parser(argparse.ArgumentParser):
    def __init__(self, program: str, name: str = None, *args, **kwargs) -> None:
        argparse.ArgumentParser.__init__(self, prog=program, *args, **kwargs)
        if name is None:
            self.name = program
        else:
            self.name = name
        self.help = False

    def add_shell(self, shell: Any) -> None:
        self.shell = shell

    def exit(self, *args, **kwargs) -> None:
        pass

    def print_usage(self, *args, **kwargs) -> None:
        try:
            self.shell.stderr.write(self.format_usage())
            self.help = True
        except AttributeError:
            pass

    def print_help(self, *args, **kwargs) -> None:
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


def convert_many(start: Union[List, Tuple, str], *args: Any) -> List[Tuple]:
    if not isinstance(start, (list, set, tuple)):
        done = [(start,) + args]
    else:
        done = [(x,) + args for x in start]
    return done
