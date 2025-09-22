from typing import Any, Optional, List, Union
from kernel.logging import logger


class Pipe:
    def __init__(
        self,
        name: str = "",
        value: Optional[List[str]] = None,
        writer: Optional[Any] = None,
        reader: Optional[Any] = None,
    ) -> None:
        if value is None:
            self.value: List[Union[str, None]] = []
        else:
            self.value = value
        self.writer = writer
        self.reader = reader
        self.name = name
        self._line = 0
        self.closed = False

    def __bool__(self) -> bool:
        return True

    def set_reader(self, callback: Any) -> None:
        self.reader = callback
        callback.stdin = self

    def set_writer(self, callback: Any) -> None:
        self.writer = callback

    def write(self, value: Any) -> None:
        if not self.closed:
            self.value.extend(str(value).split("\n"))

    def read(self) -> Any:
        for line in self.value[self._line :]:
            if line is None:
                break
            yield line
            self._line += 1

    def readline(self) -> str:
        line = self.value[self._line] if self._line < len(self.value) else None
        self._line += 1
        return line if line is not None else ""

    def readlines(self) -> List[Union[str, None]]:
        return self.value

    def close(self) -> None:
        self.closed = True
        self.value.append(None)
        self.broadcast()

    def clear(self) -> None:
        self.value = []
        self._line = 0

    def get_value(self) -> List[Union[str, None]]:
        return self.value

    def broadcast(self) -> None:
        if self.reader is not None:
            pass  # self.reader()
        else:
            if any(self.value):
                # Determine what to filter: if last element is None (pipe closed), exclude it
                if self.value and self.value[-1] is None:
                    # Pipe is closed, exclude the None terminator
                    values_to_process = self.value[:-1]
                else:
                    # Pipe is open, process all values
                    values_to_process = self.value

                # Filter out None values and empty strings
                filtered_values = [
                    str(x)
                    for x in values_to_process
                    if x is not None and x != ""
                ]

                # DEBUG: Print what we're working with
                # print(f"DEBUG broadcast: filtered_values = {filtered_values}, len = {len(filtered_values)}")
                if len(filtered_values) == 1:
                    # Single line output - add newline for consistency
                    logger.info("<%s>\n%s", self.name, filtered_values[0])
                else:
                    # Multi-line output without indentation for consistency
                    content = "\n".join(filtered_values)
                    logger.info("<%s>\n%s", self.name, content)

    def __repr__(self) -> str:
        writer_pid = getattr(self.writer, "pid", "None")
        reader_pid = getattr(self.reader, "pid", "None")
        return "<Pipe(name=%s, value=%s, writer=%s, reader=%s)>" % (
            self.name,
            self.value,
            writer_pid,
            reader_pid,
        )

    def __str__(self) -> str:
        line_value = (
            self.value[self._line] if self._line < len(self.value) else ""
        )
        return "<Pipe %d: %s>" % (self._line, line_value)
