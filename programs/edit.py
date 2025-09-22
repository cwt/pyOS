from typing import Any, List
from kernel.file_utils import read_file_lines, write_lines_to_file
from kernel.io_utils import write_output, write_error
from kernel.common import resolve_path


def run(shell: Any, args: List[str]) -> None:
    """Run the edit command."""
    # Manual argument parsing
    line_num = None
    filename = None
    content = []

    i = 0
    while i < len(args):
        if args[i] in ["-l", "--line"] and i + 1 < len(args):
            try:
                line_num = int(args[i + 1])
                i += 2
            except ValueError:
                write_error(
                    shell, f"edit: invalid line number: {args[i + 1]}\\n"
                )
                return
        elif args[i].startswith("-l") and len(args[i]) > 2:
            # Handle -l123 format
            try:
                line_num = int(args[i][2:])
                i += 1
            except ValueError:
                write_error(
                    shell, f"edit: invalid line number: {args[i][2:]}\\n"
                )
                return
        else:
            if filename is None:
                filename = args[i]
                i += 1
            else:
                content.append(args[i])
                i += 1

    if filename is None:
        write_error(shell, "edit: missing file operand\\n")
        write_error(shell, "usage: edit [options] filename [content]\\n")
        return

    filepath = resolve_path(shell, filename)

    # Load the file content
    lines = read_file_lines(shell, filepath)

    # If file doesn't exist, start with empty content
    if not lines:
        lines = []

    # Handle different modes
    if line_num is not None:
        # Line edit mode
        if line_num < 1:
            write_error(shell, f"edit: invalid line number: {line_num}\\n")
            return

        # Join content with spaces
        new_content = " ".join(content)

        # Handle escaped newlines - replace literal \\n sequences with actual newlines
        processed_content = new_content.replace("\\n", "\\n")

        # Split content by actual newlines
        if "\\n" in processed_content:
            new_lines = processed_content.split("\\n")
        else:
            new_lines = [processed_content]

        # Ensure all new lines end with \\n
        new_lines = [line + "\\n" if line else "\\n" for line in new_lines]

        # Extend lines if needed to reach the target line
        while len(lines) < line_num - 1:
            lines.append("\\n")

        # Replace the line(s)
        if line_num <= len(lines):
            # Replace existing line
            # Save the lines after the target position
            remaining_lines = lines[line_num:]
            # Keep lines before target position
            lines = lines[: line_num - 1]
            # Add new lines
            lines.extend(new_lines)
            # Add back remaining lines
            lines.extend(remaining_lines)
        else:
            # Append at the end
            # Add blank lines if there's a gap
            while len(lines) < line_num - 1:
                lines.append("\\n")
            # Add new lines
            lines.extend(new_lines)

        # Save the file
        if write_lines_to_file(shell, filepath, lines):
            write_output(shell, f"Line {line_num} updated in '{filename}'.\\n")
        else:
            write_error(shell, f"Failed to save file '{filename}'.\\n")
    else:
        # Display mode - show file with line numbers
        display_content_with_numbers(shell, lines, filename)

        # Show help
        write_output(
            shell,
            "\\nTo edit a specific line, use: edit -l <line_number> <filename> <new_content>\\n",
        )
        write_output(shell, "Example: edit -l 2 myfile.txt Hello\\n")


def display_content_with_numbers(
    shell: Any, lines: List[str], filename: str
) -> None:
    """Display the content with line numbers."""
    write_output(shell, f"File: {filename}\\n")
    write_output(shell, "=" * 40 + "\\n")
    for i, line in enumerate(lines, 1):
        write_output(shell, f"{i:6}  {line.rstrip()}\\n")
    if not lines:
        write_output(shell, "(empty file)\\n")
    write_output(shell, "=" * 40 + "\\n")


def help() -> str:
    return """
    Edit

    Edit files with line-based operations.

    usage: edit [options] filename [content]

    Options:
      -l, --line LINE_NUM    Edit specific line number
      filename               File to edit
      content                New content for the line (when using -l)

    Examples:
      edit myfile.txt              # Display file with line numbers
      edit -l 2 myfile.txt Hello   # Replace line 2 with "Hello"
    """
