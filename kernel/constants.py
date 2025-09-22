import os
import sys
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

# Check if we're running tests
_is_running_tests = "pytest" in sys.modules or "unittest" in sys.modules

# Standard file paths - use in-memory database for tests
if _is_running_tests:
    METADATAFILE = ":memory:"
    USERDATAFILE = ":memory:"
else:
    METADATAFILE = os.path.join(BASEPATH, "data/data")
    USERDATAFILE = os.path.join(BASEPATH, "data/userdata")

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
