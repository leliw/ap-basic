"""Stores data on disk in json files"""

import logging
import os
import json
from typing import Iterator, Type, Generic

from .base_storage import BaseStorage, T


class JsonFilesStorage(BaseStorage[T], Generic[T]):
    """Stores data on disk in json files

    Parameters
    ----------
    clazz: Type[T]
        The Pydantic class to store
    key_name: str
        The key name to use for the storage. Default is "id"
    base_path: str
        The base path where the json files are stored. Default is "data"
    """

    def __init__(self, clazz: Type[T], key_name: str = None, base_path="data"):
        super().__init__(clazz, key_name)
        self._base_path = base_path
        os.makedirs(self._base_path, exist_ok=True)
        self._log = logging.getLogger(__name__)

    def put(self, key: str, value: T) -> None:
        json_str = value.model_dump_json(by_alias=True, indent=2, exclude_none=True)
        with open(self._key_to_full_path(key), "w", encoding="utf-8") as file:
            file.write(json_str)

    def get(self, key: str) -> T:
        full_path = self._key_to_full_path(key)
        try:
            with open(full_path, "r", encoding="utf-8") as file:
                r = json.load(file)
            return self.clazz.model_validate(r)
        except FileNotFoundError:
            return None

    def keys(self) -> Iterator[str]:
        for k in os.listdir(self._base_path):
            yield k[:-5] if k.endswith(".json") else k

    def delete(self, key: str) -> None:
        full_path = self._key_to_full_path(key)
        os.remove(full_path)

    def _key_to_full_path(self, key: str) -> str:
        return os.path.join(self._base_path, key + ".json")
