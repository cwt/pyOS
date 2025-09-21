import threading
from typing import Optional, Any, List, Dict, TYPE_CHECKING

import kernel.stream
import kernel.system
from kernel.constants import PROGRAMSDIR, VARCHAR, BASEDIR
from kernel.exceptions import CommandNotFoundError

if TYPE_CHECKING:
    from kernel.system import System


class Shell(threading.Thread):
    def __init__(
        self,
        pid: int,
        parent: Optional["Shell"] = None,
        program: str = "interpreter",
        args: Optional[List[str]] = None,
        stdin: Optional[Any] = None,
        path: str = BASEDIR,
        system_instance: Optional["System"] = None,
    ) -> None:
        super(Shell, self).__init__()
        self.programname = program
        self.args: List[str] = args or []

        self._path = path
        self._oldpath = path
        self.parent = parent
        self.pid = pid
        self.system: kernel.system.System = (
            system_instance or kernel.system.System()
        )

        self.syscall = kernel.system.SysCall(self, self.system)

        if self.parent:
            self.vars: Dict[str, str] = self.parent.vars.copy()
            self.aliases: Dict[str, str] = self.parent.aliases.copy()
            self.prevcommands: List[str] = self.parent.prevcommands[:]
        else:
            self.vars = {
                "PATH": PROGRAMSDIR,
                "HOME": BASEDIR,
                "PWD": self._path,
                "OLDPWD": self._oldpath,
            }
            self.aliases = dict()
            self.prevcommands = []

        self.stdin = stdin
        self.stdout = kernel.stream.Pipe(name="out", writer=self)
        self.stderr = kernel.stream.Pipe(name="err", writer=self)

    def run(self) -> None:
        try:
            self.program = self.find_program(self.programname)
            if self.program:
                self.program.run(self, self.args)
        except CommandNotFoundError:
            # TODO # add back "is a directory"
            self.stderr.write("%s: command not found\n" % (self.programname,))
        # cleanup
        self.stdout.close()
        self.stderr.close()
        self.system.kill(self)

    @property
    def path(self) -> str:
        """Get the current path."""
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        """Set the current path."""
        self._oldpath = self._path
        self._path = self.sabs_path(value)

    @property
    def old_path(self) -> str:
        """Get the previous path."""
        return self._oldpath

    def sabs_path(self, path: str) -> str:
        if not path.startswith("/"):
            if path.startswith("./"):
                path = path[path.index("/") + 1 :]
            path = self.syscall.join_path(self.path, path)
        return self.syscall.iabs_path(path)

    def srel_path(self, path: str, base: Optional[str] = None) -> str:
        if base is None:
            base = self.path
        return self.syscall.rel_path(self.sabs_path(path), self.sabs_path(base))

    def program_paths(self, name: str) -> List[str]:
        if name[0:2] == "./":
            a = [self.sabs_path(name)]
        else:
            paths = self.get_var("PATH").split(":")
            a = [self.syscall.join_path(x, name) for x in paths]
        return a

    def get_var(self, name: str) -> str:
        try:
            # Handle regex match objects
            if hasattr(name, "group"):
                x = self.vars[name.group(0).lstrip(VARCHAR)]
            else:
                # Handle regular strings
                x = self.vars[name.lstrip(VARCHAR)]
        except KeyError:
            x = ""
        except Exception:
            x = ""
        return x

    def set_var(self, name: str, value: str) -> None:
        self.vars[name] = value

    def hist_find(self, value: str, start: bool = True) -> str:
        done = ""
        for x in reversed(self.prevcommands):
            if start and x.startswith(value):
                done = x
                break
            elif not start and value in x:
                done = x
                break
        return done

    def find_program(self, name: str) -> Any:
        for x in self.program_paths(name):
            if not x.endswith(".py"):
                x += ".py"
            program = self.syscall.open_program(x)
            if program:
                break
            else:
                program = self.syscall.open_program(x[:-3])
            if program:
                break
        return program

    def __repr__(self) -> str:
        return "<Shell(pid=%d, program=%s, args=%s, path=%s)>" % (
            self.pid,
            self.programname,
            self.args,
            self.path,
        )

    def __str__(self) -> str:
        return "<%s %d>" % (self.programname, self.pid)
