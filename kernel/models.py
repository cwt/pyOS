"""
Data models for pyOS using dataclasses.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Any
import datetime


@dataclass
class FileMetadata:
    """Data class for file metadata."""

    path: str
    owner: str
    permission: str
    created: datetime.datetime
    accessed: datetime.datetime
    modified: datetime.datetime

    @classmethod
    def from_tuple(cls, data: Tuple[Any, ...]) -> Optional["FileMetadata"]:
        """Create FileMetadata from database tuple."""
        if not data or len(data) < 6:
            return None
        return cls(
            path=data[0],
            owner=data[1],
            permission=data[2],
            created=data[3],
            accessed=data[4],
            modified=data[5],
        )


@dataclass
class UserData:
    """Data class for user data."""

    username: str
    groupname: str
    info: str
    homedir: str
    shell: str
    password: str

    @classmethod
    def from_tuple(cls, data: Tuple[Any, ...]) -> Optional["UserData"]:
        """Create UserData from database tuple."""
        if not data or len(data) < 6:
            return None
        return cls(
            username=data[0],
            groupname=data[1],
            info=data[2],
            homedir=data[3],
            shell=data[4],
            password=data[5],
        )
