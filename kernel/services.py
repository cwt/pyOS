"""
Service classes for pyOS operations.
"""

from typing import Any, List, Optional, Union, Dict, Tuple
from kernel.models import FileMetadata, UserData
from kernel.protocols import FilesystemProtocol, MetadataProtocol, UserProtocol


class FilesystemService:
    """Service class for filesystem operations."""

    def __init__(self, filesystem_module: FilesystemProtocol) -> None:
        self.fs = filesystem_module

    def abs_path(self, path: str) -> str:
        return self.fs.abs_path(path)

    def rel_path(self, path: str, base: str) -> str:
        return self.fs.rel_path(path, base)

    def irel_path(self, path: str) -> str:
        return self.fs.irel_path(path)

    def iabs_path(self, path: str) -> str:
        return self.fs.iabs_path(path)

    def dir_name(self, path: str) -> str:
        return self.fs.dir_name(path)

    def base_name(self, path: str) -> str:
        return self.fs.base_name(path)

    def split(self, path: str) -> Tuple[str, str]:
        return self.fs.split(path)

    def join_path(self, *args: str) -> str:
        return self.fs.join_path(*args)

    def exists(self, path: str) -> bool:
        return self.fs.exists(path)

    def is_file(self, path: str) -> bool:
        return self.fs.is_file(path)

    def is_dir(self, path: str) -> bool:
        return self.fs.is_dir(path)

    def copy(self, src: str, dst: str) -> None:
        self.fs.copy(src, dst)

    def remove(self, path: str) -> None:
        self.fs.remove(path)

    def remove_dir(self, path: str) -> None:
        self.fs.remove_dir(path)

    def get_size(self, path: str) -> int:
        return self.fs.get_size(path)

    def list_dir(self, path: str) -> List[str]:
        return self.fs.list_dir(path)

    def list_glob(self, expression: str) -> List[str]:
        return self.fs.list_glob(expression)

    def list_all(self, path: str = "/") -> List[str]:
        return self.fs.list_all(path)

    def make_dir(self, path: str) -> None:
        self.fs.make_dir(path)

    def open_file_context(self, path: str, mode: str) -> Any:
        return self.fs.open_file_context(path, mode)

    def open_file(self, path: str, mode: str) -> Any:
        return self.fs.open_file(path, mode)

    def open_program(self, path: str) -> Any:
        return self.fs.open_program(path)


class MetadataService:
    """Service class for metadata operations."""

    def __init__(self, metadata_module: MetadataProtocol) -> None:
        self.md = metadata_module

    def get_meta_data(self, path: str) -> Optional[FileMetadata]:
        return self.md.get_meta_data(path)

    def get_all_meta_data(
        self, path: str = "/"
    ) -> Optional[List[FileMetadata]]:
        return self.md.get_all_meta_data(path)

    def add_path(self, path: str, owner: str, permission: str) -> None:
        self.md.add_path(path, owner, permission)

    def copy_path(self, src: str, dst: str) -> None:
        self.md.copy_path(src, dst)

    def move_path(self, src: str, dst: str) -> None:
        self.md.move_path(src, dst)

    def delete_path(self, path: str) -> None:
        self.md.delete_path(path)

    def get_permission_string(self, path: str) -> str:
        return self.md.get_permission_string(path)

    def get_permission_number(self, path: str) -> str:
        return self.md.get_permission_number(path)

    def set_permission_string(self, path: str, value: str) -> None:
        self.md.set_permission_string(path, value)

    def set_permission_number(self, path: str, value: str) -> None:
        self.md.set_permission_number(path, value)

    def set_permission(self, path: str, value: Union[str, int]) -> None:
        self.md.set_permission(path, value)

    def set_time(
        self,
        path: str,
        value: Optional[
            Union[Dict[str, Any], str, Tuple[Any, ...], List[Any]]
        ] = None,
    ) -> None:
        self.md.set_time(path, value)

    def set_time_list(
        self, path: str, value: Union[Tuple[Any, ...], List[Any]]
    ) -> None:
        self.md.set_time_list(path, value)

    def set_time_dict(
        self, path: str, value: Optional[Dict[str, Any]] = None
    ) -> None:
        self.md.set_time_dict(path, value)

    def set_time_string(self, path: str, value: Optional[str] = None) -> None:
        self.md.set_time_string(path, value)

    def get_time(self, path: str) -> Tuple[Any, ...]:
        return self.md.get_time(path)

    def get_owner(self, path: str) -> str:
        return self.md.get_owner(path)

    def set_owner(self, path: str, owner: str) -> None:
        self.md.set_owner(path, owner)


class UserService:
    """Service class for user operations."""

    def __init__(self, userdata_module: UserProtocol) -> None:
        self.ud = userdata_module

    def get_user_data(self, user: str) -> Optional[UserData]:
        return self.ud.get_user_data(user)

    def get_all_user_data(self) -> Optional[List[UserData]]:
        return self.ud.get_all_user_data()

    def add_user(
        self,
        user: str,
        group: str,
        info: str,
        homedir: str,
        shell: str,
        password: str,
    ) -> None:
        self.ud.add_user(user, group, info, homedir, shell, password)

    def delete_user(self, user: str) -> None:
        self.ud.delete_user(user)

    def change_user(self, user: str, value: Any) -> None:
        self.ud.change_user(user, value)

    def get_group(self, user: str) -> str:
        return self.ud.get_group(user)

    def set_group(self, user: str, value: str) -> None:
        self.ud.set_group(user, value)

    def get_info(self, user: str) -> str:
        return self.ud.get_info(user)

    def set_info(self, user: str, value: str) -> None:
        self.ud.set_info(user, value)

    def get_homedir(self, user: str) -> str:
        return self.ud.get_homedir(user)

    def set_homedir(self, user: str, value: str) -> None:
        self.ud.set_homedir(user, value)

    def get_shell(self, user: str) -> str:
        return self.ud.get_shell(user)

    def set_shell(self, user: str, value: str) -> None:
        self.ud.set_shell(user, value)

    def get_password(self, user: str) -> str:
        return self.ud.get_password(user)

    def set_password(self, user: str, value: str) -> None:
        self.ud.set_password(user, value)

    def correct_password(self, user: str, password: str) -> bool:
        return self.ud.correct_password(user, password)
