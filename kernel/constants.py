import os
from typing import Final, List
from enum import IntEnum


class SystemState(IntEnum):
    """Enumeration of system states."""

    REBOOT = -2
    SHUTDOWN = -1
    IDLE = 0
    RUNNING = 1


OSNAME: Final[str] = "pyOS"

# The start of the virtual filesystem
BASEPATH: Final[str] = os.getcwd()

# Standard system paths
BASEDIR: Final[str] = "/"
CURRENTDIR: Final[str] = "."
PARENTDIR: Final[str] = ".."
PROGRAMSDIR: Final[str] = "/programs"
KERNELDIR: Final[str] = "/kernel"
METADIR: Final[str] = "/meta"  # need to implement
USERDIR: Final[str] = "/user"  # need to implement
SYSDATADIR: Final[str] = "/data"

# Standard file paths
METADATAFILE: Final[str] = os.path.join(BASEPATH, "data/data")
USERDATAFILE: Final[str] = os.path.join(BASEPATH, "data/userdata")

# Special Characters/strings
VARCHAR: Final[str] = "$"
PATHCHAR: Final[str] = "/"
PIPECHAR: Final[str] = "|"
OUTCHAR: Final[str] = ">"
APPENDCHAR: Final[str] = ">>"
INCHAR: Final[str] = "<"

# System State Vars
REBOOT: Final[int] = -2
SHUTDOWN: Final[int] = -1
IDLE: Final[int] = 0
RUNNING: Final[int] = 1

# Development Vars
IGNORREFILES: Final[List[str]] = [".pyc", ".git"]
