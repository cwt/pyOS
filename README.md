pyOS
====
pyOS (prounounced "pious") is a python implemention of a psuedo unix-like operating system.

Requirements
-------------
- Python 3.10+

Features
--------
- unix terminal interface
- common utilities (cp, mv, rm, ls, cat, head, sed, etc)
- piping and stdio redirection
- semi virtual filesystem
- file/directory metadata
- dynamic manipulation of files
- basic system call structure
- file/directory permissions
- basic user system
- DRY code principles with utility modules for common operations

Utility Modules
---------------
- `kernel.common` - Common utility functions for file operations and error handling
- `kernel.file_utils` - File operation utilities for reading, writing, and processing files
- `kernel.io_utils` - Standard input/output utilities for consistent I/O operations
- `kernel.path_utils` - Path manipulation utilities for handling file paths
- `kernel.metadata` - Enhanced database operations for file metadata
- `kernel.userdata` - Enhanced database operations for user data

Todo
----
- sdterr redirection
- other utilities (xargs, edit(ed?), awk, etc)
- polish utilities
- formalize the directory structure
- thread(multiprocess?) processes
- exit codes
- tests
- documentation
- formalize syscalls
- networking
- \`command\` execution
- user commands (add, delete, change permissions, etc)

Setup
-----
- cd into the pyOS directory
- run pyOS.py