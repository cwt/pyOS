from typing import Any, Optional, List, Union


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
        return bool(self.reader)

    def set_reader(self, callback: Any) -> None:
        self.reader = callback
        callback.stdin = self

    def set_writer(self, callback: Any) -> None:
        self.writer = callback

    def write(self, value: Any) -> None:
        if not self.closed:
            self.value.extend(str(value).split("\n"))

    def read(self) -> Any:
        line = ""
        while line is not None:
            for line in self.value[self._line :]:
                if line is None:
                    break
                yield line
                self._line += 1

    def readline(self) -> str:
        line = self.value[self._line]
        self._line += 1
        return line

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
                print(
                    "<%s> %s"
                    % (self.name, "\n".join(str(x) for x in self.value[:-1])),
                    end=" ",
                )

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
        return "<Pipe %d: %s>" % (self._line, self.value[self._line])
