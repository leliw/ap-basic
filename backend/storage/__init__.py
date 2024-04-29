"""Siple file based storage"""
from .base_storage import T, KeyNotExists, BaseStorage
from .json_files_storage import JsonFilesStorage
from .directory_storage import DirectoryStorage
