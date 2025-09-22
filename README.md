pyOS
====
pyOS (pronounced "pious") is a Python implementation of a pseudo unix-like operating system.

Requirements
-------------
- Python 3.10+

Features
--------
- Unix terminal interface with command interpreter
- Common utilities (cat, cd, cp, echo, find, grep, head, ls, mkdir, mv, pwd, rm, sed, tail, tee, touch, tree, which, etc)
- Piping and stdio redirection
- Virtual filesystem with persistent storage
- File/directory metadata including timestamps and permissions
- Dynamic manipulation of files and directories
- System call interface for program access to OS functions
- File/directory permissions with owner/group/other access controls
- Basic user system with authentication
- Environment variables and command aliases
- Command history
- DRY code principles with utility modules for common operations

Architecture
------------
The system is composed of several key components:

- **Kernel**: Core system services and protocols
  - System management (startup, shutdown, process management)
  - Shell implementation with environment and variable support
  - Stream system for pipes and I/O redirection
  - Filesystem abstraction layer
  - Metadata and user data management
  - Permission checking system
  - Common utility modules for file, I/O, and path operations

- **Programs**: Individual command implementations in the `programs/` directory
  - Standard Unix utilities (ls, cat, cp, etc)
  - System management commands (login, logout, shutdown, restart)
  - Utility commands (echo, find, grep, etc)

Utility Modules
---------------
- `kernel.base_command` - Base class for implementing commands
- `kernel.common` - Common utility functions for file operations and error handling
- `kernel.constants` - System constants and enumerations
- `kernel.exceptions` - Custom exception classes
- `kernel.file_utils` - File operation utilities for reading, writing, and processing files
- `kernel.filesystem` - Filesystem abstraction layer
- `kernel.interfaces` - Interface definitions for system components
- `kernel.io_utils` - Standard input/output utilities for consistent I/O operations
- `kernel.logging` - Logging utilities
- `kernel.metadata` - Enhanced database operations for file metadata
- `kernel.models` - Data models for system objects
- `kernel.path_utils` - Path manipulation utilities for handling file paths
- `kernel.permissions` - Permission checking decorators and utilities
- `kernel.protocols` - Protocol definitions for system components
- `kernel.services` - Service layer implementations
- `kernel.shell` - Shell implementation with environment and variable support
- `kernel.stream` - Stream system for pipes and I/O redirection
- `kernel.system` - Core system services and SysCall interface
- `kernel.userdata` - Enhanced database operations for user data
- `kernel.utils` - Additional utility functions

Implemented Utilities
---------------------
- `alias` - Manage command aliases
- `cat` - Concatenate and print files
- `cd` - Change directory
- `cp` - Copy files and directories
- `echo` - Display a line of text
- `edit` - Simple text editor
- `find` - Search for files in a directory hierarchy
- `grep` - Print lines matching a pattern
- `head` - Output the first part of files
- `help` - Display help information
- `history` - Command history
- `interpreter` - Command interpreter
- `login` - User authentication
- `logout` - End user session
- `ls` - List directory contents
- `mkdir` - Make directories
- `mv` - Move/rename files
- `pwd` - Print working directory
- `restart` - Restart the system
- `rm` - Remove files or directories
- `sed` - Stream editor for filtering and transforming text
- `shutdown` - Shutdown the system
- `tac` - Print files in reverse
- `tail` - Output the last part of files
- `tee` - Read from standard input and write to standard output and files
- `touch` - Change file timestamps or create empty files
- `tree` - List contents of directories in a tree-like format
- `which` - Locate a command
- `write` - Write input to a file

Todo
----
- stderr redirection
- Additional utilities (xargs, awk, etc)
- Polish existing utilities
- Formalize the directory structure
- Thread(multiprocess?) processes
- Exit codes
- Tests
- Documentation
- Formalize syscalls
- Networking
- \`command\` execution
- User management commands (add, delete, change permissions, etc)

Setup
-----
1. cd into the pyOS directory
2. Run `python pyOS.py` to start the system
3. Use `--login` and `--password` arguments for automatic login during development