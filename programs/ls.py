import argparse
from kernel.utils import Parser
from typing import Any, List
from kernel.base_command import BaseCommand
from kernel.common import resolve_path, handle_file_operation
from kernel.models import FileMetadata


class LsCommand(BaseCommand):
    """List directory contents."""

    def __init__(self) -> None:
        super().__init__("ls", "List directory contents")
        self.parser = Parser(
            "ls",
            name="List Directory",
            description="Returns the contents of a directory.",
        )
        pa = self.parser.add_argument
        pa("paths", type=str, nargs="*")
        pa("-l", action="store_true", dest="long", default=False)
        pa("-a", action="store_true", dest="all", default=False)

    def run(self, shell: Any, args: List[str]) -> None:
        self.parser.add_shell(shell)
        parsed_args = self.parser.parse_args(args)
        if not self.parser.help:
            if parsed_args.paths:
                paths = parsed_args.paths
            else:
                paths = [shell.path]
            for relpath in sorted(paths):
                self._ls(shell, relpath, parsed_args)

    def _ls(self, shell: Any, relpath: str, args: argparse.Namespace) -> None:
        fsgm = shell.syscall.get_meta_data
        fsbn = shell.syscall.base_name
        format_str = "%s %s %s %s"
        path = resolve_path(shell, relpath)
        if handle_file_operation(shell, path, "exists"):
            try:
                # Check if the path is a file or directory
                if handle_file_operation(shell, path, "is_file"):
                    # Handle single file case
                    metadata = fsgm(path)
                    if args.long and metadata is not None:
                        # Handle both FileMetadata objects and tuples for backward compatibility
                        if isinstance(metadata, FileMetadata):
                            # FileMetadata object
                            permission = metadata.permission
                            owner = metadata.owner
                            item_path = metadata.path
                        else:
                            # Tuple (from tests)
                            permission, owner, item_path = (
                                metadata[2],
                                metadata[1],
                                metadata[0],
                            )
                        output_line = format_str % (
                            permission,
                            owner,
                            "1",
                            fsbn(item_path),
                        )
                        shell.stdout.write(output_line)
                    else:
                        # Just print the filename for non-long format
                        shell.stdout.write(fsbn(path))
                else:
                    # Handle directory case (existing logic)
                    a = shell.syscall.list_dir(path)
                    if args.long:
                        b = [
                            fsgm(
                                resolve_path(
                                    shell, shell.syscall.join_path(path, x)
                                )
                            )
                            for x in a
                        ]
                        # Access attributes from FileMetadata objects or tuples, filtering out None values
                        a = []
                        for item in b:
                            if item is not None:
                                # Handle both FileMetadata objects and tuples for backward compatibility
                                if isinstance(item, FileMetadata):
                                    # FileMetadata object
                                    permission = item.permission
                                    owner = item.owner
                                    item_path = item.path
                                else:
                                    # Tuple (from tests)
                                    permission, owner, item_path = (
                                        item[2],
                                        item[1],
                                        item[0],
                                    )
                                a.append(
                                    format_str
                                    % (permission, owner, "1", fsbn(item_path))
                                )

                    if len(args.paths) > 1:
                        shell.stdout.write("%s:" % (relpath,))
                    if shell.stdout or args.long:
                        shell.stdout.write("\n".join(a))
                    else:
                        if a:
                            maxlen = max(max([len(x) for x in a]), 1)
                            # arbitrary line length
                            columns = (80 // maxlen) - 1
                            b = []
                            for i, x in enumerate(a):
                                newline = (
                                    "\n" if not ((i + 1) % columns) else ""
                                )
                                if not ((i + 1) % columns):
                                    newline = "\n"
                                    spacing = ""
                                else:
                                    newline = ""
                                    spacing = " " * (maxlen - len(x) + 1)
                                b.append(x + spacing + newline)
                            output = "".join(b).rstrip()
                            shell.stdout.write(output)
                            if output:  # Only add newline if there was output
                                shell.stdout.write("\n")
                    if len(args.paths) > 1:
                        shell.stdout.write("\n")
            except OSError:
                shell.stderr.write(
                    "ls: cannot acces %s: no such file or directory\n"
                    % (relpath,)
                )
        else:
            shell.stderr.write(
                "ls: cannot acces %s: no such file or directory\n" % (relpath,)
            )

    def help(self) -> str:
        return self.parser.help_msg()


# Create a singleton instance for backward compatibility
command = LsCommand()


def run(shell: Any, args: List[str]) -> None:
    """Backward compatibility function."""
    command.run(shell, args)


def help() -> str:
    """Backward compatibility function."""
    return command.help()
