import sys
import kernel.filesystem
import kernel.metadata
import kernel.userdata

import kernel.shell
from kernel.constants import KERNELDIR, SystemState
from kernel.services import FilesystemService, MetadataService, UserService
from kernel.permissions import PermissionChecker
from kernel.protocols import (
    SystemProtocol,
    FilesystemProtocol,
    MetadataProtocol,
    UserProtocol,
)
from typing import Dict, Any, List, Optional, TYPE_CHECKING, Union, Tuple

if TYPE_CHECKING:
    from kernel.models import FileMetadata, UserData
else:
    # For runtime imports
    from kernel.models import FileMetadata, UserData


class System(SystemProtocol):
    """
    Handles all of the low level stuff.
    PIDs, startup, shutdown, events

    System States:
    -2: reboot
    -1: shutting down
    0:  idle
    1:  running shell
    """

    def __init__(
        self, filesystem: Any = None, metadata: Any = None, userdata: Any = None
    ) -> None:
        self.display = None  # Display()

        self._filesystem = filesystem or kernel.filesystem
        self._metadata = metadata or kernel.metadata
        self._userdata = userdata or kernel.userdata

        self.pids: List[int] = []
        self._state = SystemState.IDLE

        # Auto-login attributes for testing
        self._auto_login_user: Optional[str] = None
        self._auto_login_password: Optional[str] = None

    @property
    def filesystem(self) -> FilesystemProtocol:
        return self._filesystem

    @property
    def metadata(self) -> MetadataProtocol:
        return self._metadata

    @property
    def userdata(self) -> UserProtocol:
        return self._userdata

    @property
    def state(self) -> SystemState:
        return self._state

    @state.setter
    def state(self, value: SystemState) -> None:
        self._state = value

    def run(self) -> None:
        if "pytest" not in sys.modules:
            self.startup()
        self.state = SystemState.IDLE
        while self.state >= SystemState.IDLE:
            current = self.new_shell(program="login")
            current.run()
        self.shutdown()
        if self.state == SystemState.REBOOT:
            self.run()

    def startup(self) -> None:
        path = self.filesystem.join_path(KERNELDIR, "startup.py")
        program = self.filesystem.open_program(path)
        program.run()

    def shutdown(self) -> None:
        path = self.filesystem.join_path(KERNELDIR, "shutdown.py")
        program = self.filesystem.open_program(path)
        program.run()

    def new_shell(self, *args: Any, **kwargs: Any) -> Any:
        kwargs["system_instance"] = self
        y = kernel.shell.Shell(len(self.pids), *args, **kwargs)
        self.new_pid(y)
        self.state = SystemState.RUNNING
        return y

    def get_pid(self, item: Any) -> Optional[int]:
        try:
            x = self.pids.index(item)
        except Exception:
            x = None
        return x

    def get_process(self, pid: int) -> Any:
        try:
            x = self.pids[pid]
        except Exception:
            x = None
        return x

    def new_pid(self, item: Any) -> int:
        x = len(self.pids)
        self.pids.append(item)
        return x

    def get_events(self, _type: Any = None) -> str:
        if _type is None:
            return "all"
        else:
            return "some"

    def kill(self, shell: Any) -> None:
        try:
            self.pids.remove(shell)
        except ValueError:
            # Shell not in list, ignore
            pass


def compare_permission(
    path: str,
    user: str,
    access: Union[int, str],
    system_instance: Optional["System"] = None,
) -> bool:
    system = system_instance or System()
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


def has_permission(
    path: str,
    user: str,
    access: Union[int, str],
    system_instance: Optional["System"] = None,
) -> bool:
    system = system_instance or System()
    dirpaths = [path]
    temppath = path
    while temppath != "/":
        temppath = system.filesystem.dir_name(temppath)
        dirpaths.append(temppath)
    if not all(compare_permission(x, user, 5, system) for x in dirpaths[1:]):
        # does not have read permissions all the way to path
        return False

    if system.filesystem.is_dir(dirpaths[0]):
        if not compare_permission(dirpaths[0], user, access, system):
            # does not have access permissions on folder
            return False
    else:
        if not compare_permission(dirpaths[1], user, access, system):
            # does not have access permissions for containing folder
            return False
        try:
            compare_permission(dirpaths[0], user, access, system)
        except TypeError:
            if access != "w":
                # TODO # maybe remove?
                # you can not read a file that does not exist
                return False
    return True


class SysCall(object):
    def __init__(
        self,
        shell: "kernel.shell.Shell",
        system_instance: Optional["System"] = None,
    ) -> None:
        self.system: System = system_instance or System()
        self.fs_service = FilesystemService(self.system.filesystem)
        self.md_service = MetadataService(self.system.metadata)
        self.ud_service = UserService(self.system.userdata)
        self.shell = shell

    def abs_path(self, path: str) -> str:
        return self.fs_service.abs_path(path)

    def rel_path(self, path: str, base: str) -> str:
        return self.fs_service.rel_path(path, base)

    def irel_path(self, path: str) -> str:
        return self.fs_service.irel_path(path)

    def iabs_path(self, path: str) -> str:
        return self.fs_service.iabs_path(path)

    def dir_name(self, path: str) -> str:
        return self.fs_service.dir_name(path)

    def base_name(self, path: str) -> str:
        return self.fs_service.base_name(path)

    def split(self, path: str) -> Tuple[str, str]:
        return self.fs_service.split(path)

    def join_path(self, *args: str) -> str:
        return self.fs_service.join_path(*args)

    #############################################

    @PermissionChecker("r")
    def exists(self, path: str) -> bool:
        return self.fs_service.exists(path)

    @PermissionChecker("r")
    def is_file(self, path: str) -> bool:
        return self.fs_service.is_file(path)

    @PermissionChecker("r")
    def is_dir(self, path: str) -> bool:
        return self.fs_service.is_dir(path)

    @PermissionChecker("rw")
    def copy(self, src: str, dst: str) -> None:
        self.fs_service.copy(src, dst)
        self.md_service.copy_path(src, dst)

    @PermissionChecker("w")
    def remove(self, path: str) -> None:
        self.fs_service.remove(path)
        self.md_service.delete_path(path)

    @PermissionChecker("w")
    def remove_dir(self, path: str) -> None:
        self.fs_service.remove_dir(path)
        self.md_service.delete_path(path)

    @PermissionChecker("r")
    def get_size(self, path: str) -> int:
        return self.fs_service.get_size(path)

    @PermissionChecker("r")
    def list_dir(self, path: str) -> List[str]:
        return self.fs_service.list_dir(path)

    @PermissionChecker("r")
    def list_glob(self, expression: str) -> List[str]:
        return self.fs_service.list_glob(expression)

    @PermissionChecker("r")  # ? #
    def list_all(self, path: str = "/") -> List[str]:
        listing = [path]
        for x in self.list_dir(path):
            new = self.join_path(path, x)
            if self.is_dir(new):
                listing.extend(self.list_all(new))
            else:
                listing.append(new)
        return listing

    @PermissionChecker("w")
    def make_dir(self, path: str) -> None:
        self.fs_service.make_dir(path)
        self.md_service.add_path(path, "root", "rwxrwxrwx")

    @PermissionChecker("1")
    def open_file(self, path: str, mode: str) -> Any:
        temp = self.fs_service.is_file(path)
        x = FileDecorator(self.fs_service.open_file(path, mode), path)
        if not temp:
            self.md_service.add_path(path, "root", "rwxrwxrwx")
        return x

    @PermissionChecker("x")
    def open_program(self, path: str) -> Any:
        return self.fs_service.open_program(path)

    #############################################

    @PermissionChecker("r")
    def get_meta_data(self, path: str) -> Optional[FileMetadata]:
        return self.md_service.get_meta_data(path)

    @PermissionChecker("r")  # ? #
    def get_all_meta_data(
        self, path: str = "/"
    ) -> Optional[List[FileMetadata]]:
        return self.md_service.get_all_meta_data(path)

    @PermissionChecker("r")
    def get_permission_string(self, path: str) -> str:
        return self.md_service.get_permission_string(path)

    @PermissionChecker("r")
    def get_permission_number(self, path: str) -> str:
        return self.md_service.get_permission_number(path)

    @PermissionChecker("w")
    def set_permission_string(self, path: str, value: str) -> None:
        return self.md_service.set_permission_string(path, value)

    @PermissionChecker("w")
    def set_permission_number(self, path: str, value: str) -> None:
        return self.md_service.set_permission_number(path, value)

    @PermissionChecker("w")
    def set_permission(self, path: str, value: Union[str, int]) -> None:
        return self.md_service.set_permission(path, value)

    @PermissionChecker("w")
    def set_time(
        self,
        path: str,
        value: Optional[
            Union[Dict[str, Any], str, Tuple[Any, ...], List[Any]]
        ] = None,
    ) -> None:
        return self.md_service.set_time(path, value)

    @PermissionChecker("w")
    def set_time_list(
        self, path: str, value: Union[Tuple[Any, ...], List[Any]]
    ) -> None:
        return self.md_service.set_time_list(path, value)

    @PermissionChecker("w")
    def set_time_dict(
        self, path: str, value: Optional[Dict[str, Any]] = None
    ) -> None:
        return self.md_service.set_time_dict(path, value)

    @PermissionChecker("w")
    def set_time_string(self, path: str, value: Optional[str] = None) -> None:
        return self.md_service.set_time_string(path, value)

    @PermissionChecker("r")
    def get_time(self, path: str) -> Tuple[Any, ...]:
        return self.md_service.get_time(path)

    @PermissionChecker("r")
    def get_owner(self, path: str) -> str:
        return self.md_service.get_owner(path)

    @PermissionChecker("w")
    def set_owner(self, path: str, owner: str) -> None:
        return self.md_service.set_owner(path, owner)

    def correct_password(self, user: str, password: str) -> bool:
        return self.ud_service.correct_password(user, password)

    #############################################

    def get_user_data(self, user: str) -> Optional[UserData]:
        return self.ud_service.get_user_data(user)

    def get_all_user_data(self) -> Optional[List[UserData]]:
        return self.ud_service.get_all_user_data()

    def add_user(
        self,
        user: str,
        group: str,
        info: str,
        homedir: str,
        shell: str,
        password: str,
    ) -> None:
        return self.ud_service.add_user(
            user, group, info, homedir, shell, password
        )

    def delete_user(self, user: str) -> None:
        return self.ud_service.delete_user(user)

    def change_user(self, user: str, value: Any) -> None:
        return self.ud_service.change_user(user, value)

    def get_group(self, user: str) -> str:
        return self.ud_service.get_group(user)

    def set_group(self, user: str, value: str) -> None:
        return self.ud_service.set_group(user, value)

    def get_info(self, user: str) -> str:
        return self.ud_service.get_info(user)

    def set_info(self, user: str, value: str) -> None:
        return self.ud_service.set_info(user, value)

    def get_homedir(self, user: str) -> str:
        return self.ud_service.get_homedir(user)

    def set_homedir(self, user: str, value: str) -> None:
        return self.ud_service.set_homedir(user, value)

    def get_shell(self, user: str) -> str:
        return self.ud_service.get_shell(user)

    def set_shell(self, user: str, value: str) -> None:
        return self.ud_service.set_shell(user, value)

    def get_password(self, user: str) -> str:
        return self.ud_service.get_password(user)

    def set_password(self, user: str, value: str) -> None:
        return self.ud_service.set_password(user, value)


class FileDecorator(object):
    def __init__(
        self, f: Any, name: str, metadata_service: Optional[Any] = None
    ) -> None:
        self.__f = f
        self.__name = name
        if metadata_service is not None:
            self._metadata_service = metadata_service
        else:
            # Get the metadata service from the System singleton
            system = System()
            self._metadata_service = MetadataService(system.metadata)
        self._metadata_service.set_time(self.name, "an")

    def close(self) -> None:
        self._metadata_service.set_time(self.name, "mn")
        self.__f.close()

    @property
    def name(self) -> str:
        return self.__name

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__f, name)

    def __iter__(self) -> Any:
        return self.__f.__iter__()

    def __repr__(self) -> str:
        result = self.__f.__repr__()
        return str(result) if result is not None else ""

    def __enter__(self) -> Any:
        return self.__f.__enter__()

    def __exit__(self, *excinfo: Any) -> Any:
        return self.__f.__exit__(*excinfo)
