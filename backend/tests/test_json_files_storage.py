import unittest
import shutil
from pydantic import BaseModel

from storage import JsonFilesStorage

class T(BaseModel):
    a: int
    b: int

class TestJsonFilesStorage(unittest.TestCase):

    STORAGE_PATH = "tests/tmp/basic_storage"

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.STORAGE_PATH, ignore_errors=True)
        return super().tearDownClass()
    
    def test_basic_storage_pydantic(self):
        storage = JsonFilesStorage(T, base_path=self.STORAGE_PATH)
        t = T(a=1, b=2)
        storage.put('key', t)
        self.assertEqual(storage.get('key'), T(a=1, b=2))
        self.assertEqual(list(storage.keys()), ['key'])
        storage.delete('key')
        self.assertIsNone(storage.get('key'))

if __name__ == '__main__':
    unittest.main()