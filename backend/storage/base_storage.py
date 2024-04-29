"""Base class for storage implementations which store Pydantic objects"""

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Iterator, Type, TypeVar, Generic

T = TypeVar("T", bound=BaseModel)


class KeyNotExists(Exception):
    """Raised when key is not found"""


class BaseStorage(ABC, Generic[T]):
    """Base class for storage implementations which store Pydantic objects

    Parameters:
    ----------
    clazz: Type[T]
        The Pydantic class to store
    key_name: str
        The key name to use for the storage. Default is "id"
    """

    def __init__(self, clazz: Type[T], key_name: str = None):
        self.clazz = clazz
        self.key_name = key_name if key_name else "id"

    @abstractmethod
    def put(self, key: str, value: T) -> None:
        """Store the value with the key"""
        pass

    def save(self, value: T) -> None:
        """Store the value with the key from the value itself"""
        key = getattr(value, self.key_name)
        self.put(key, value)

    @abstractmethod
    def get(self, key: str) -> T:
        """Get the value with the key"""
        pass

    @abstractmethod
    def keys(self) -> Iterator[T]:
        """Get all the keys"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete the value with the key"""
        pass

    def drop(self) -> None:
        """Delete all the values"""
        for key in self.keys():
            self.delete(key)

    def get_all(self) -> Iterator[T]:
        """Get all the values"""
        for key in self.keys():
            yield self.get(key)
