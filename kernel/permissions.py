"""
Elegant permission checking decorators for pyOS.
"""

from functools import wraps
from typing import Callable, Any, Union
from kernel.logging import logger


class PermissionChecker:
    """Elegant permission checking decorator."""

    def __init__(self, *permissions: str) -> None:
        """Initialize the permission checker.

        Args:
            *permissions: Permission requirements for each argument.
                         Use 'r' for read, 'w' for write, 'x' for execute.
                         Use digits to reference other arguments (e.g., '1' means use permission from args[1]).
        """
        self.permissions = permissions

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator implementation."""

        @wraps(func)
        def wrapper(instance: Any, *args: Any, **kwargs: Any) -> Any:
            # Get the system instance from the instance
            system = getattr(instance, "system", None)
            if not system:
                # Try to get system from shell if this is a syscall
                shell = getattr(instance, "shell", None)
                if shell:
                    system = getattr(shell, "system", None)

            if not system:
                logger.warning(
                    "No system instance found for permission checking"
                )
                return func(instance, *args, **kwargs)

            # Check permissions for each argument based on the permissions list
            for i, permission in enumerate(self.permissions):
                if i >= len(args):
                    break

                path = args[i]

                # If permission is a digit, it refers to another argument
                if permission.isdigit():
                    perm_index = int(permission)
                    if perm_index < len(args):
                        # Get the actual permission from the referenced argument
                        permission = self._extract_permission_from_arg(
                            args[perm_index]
                        )
                    else:
                        permission = "r"  # Default to read permission

                # Check the permission
                if self._has_permission(path, "root", permission, system):
                    logger.info(
                        "root %s has permission for %s", permission, path
                    )
                else:
                    logger.warning(
                        "root %s permission denied for %s", permission, path
                    )

            return func(instance, *args, **kwargs)

        return wrapper

    def _extract_permission_from_arg(self, arg: Any) -> str:
        """Extract permission from an argument.

        Args:
            arg: The argument to extract permission from

        Returns:
            The extracted permission ('r', 'w', or 'x')
        """
        if isinstance(arg, str):
            # If arg is a string, try to extract permission from common mode strings
            if "w" in arg:
                return "w"
            elif "r" in arg:
                return "r"
            elif "x" in arg:
                return "x"
        # Default to read permission
        return "r"

    def _has_permission(
        self, path: str, user: str, access: str, system: Any
    ) -> bool:
        """Check if a user has permission for a path.

        Args:
            path: The path to check
            user: The user to check permissions for
            access: The access type ('r', 'w', 'x')
            system: The system instance

        Returns:
            True if the user has permission, False otherwise
        """
        dirpaths = [path]
        temppath = path
        while temppath != "/":
            temppath = system.filesystem.dir_name(temppath)
            dirpaths.append(temppath)
        if not all(
            self._compare_permission(x, user, 5, system) for x in dirpaths[1:]
        ):
            # does not have read permissions all the way to path
            return False

        if system.filesystem.is_dir(dirpaths[0]):
            if not self._compare_permission(dirpaths[0], user, access, system):
                # does not have access permissions on folder
                return False
        else:
            if not self._compare_permission(dirpaths[1], user, access, system):
                # does not have access permissions for containing folder
                return False
            try:
                self._compare_permission(dirpaths[0], user, access, system)
            except TypeError:
                if access != "w":
                    # you can not read a file that does not exist
                    return False
        return True

    def _compare_permission(
        self, path: str, user: str, access: Union[int, str], system: Any
    ) -> bool:
        """Compare permissions for a path.

        Args:
            path: The path to check
            user: The user to check permissions for
            access: The access type (int or string)
            system: The system instance

        Returns:
            True if the user has the specified permission, False otherwise
        """
        metadata = system.metadata.get_meta_data(path)
        if not metadata:
            return False

        owner = metadata.owner
        permissions = system.metadata.get_permission_number(path)
        if isinstance(access, int):
            compare = [access * (user == owner), 0, access]
        else:
            d = {"r": 4, "w": 2, "x": 1}
            compare = [d[access] * (owner == user), 0, d[access]]
        return any(int(x) & y for (x, y) in zip(permissions, compare))


# Convenience decorators
read_permission = PermissionChecker("r")
write_permission = PermissionChecker("w")
execute_permission = PermissionChecker("x")
read_write_permission = PermissionChecker("rw")
