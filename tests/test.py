import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from files import object_exists, hash_object, get_object

class TestFiles(unittest.TestCase):

    def test_object_exists(self):
        self.assertTrue(object_exists('some_existing_object_id'))
        self.assertFalse(object_exists('non_existing_object_id'))

    def test_hash_object(self):
        data = b"test data"
        obj_id = hash_object(data)
        self.assertEqual(len(obj_id), 40)  # SHA-1 hash length

    def test_get_object(self):
        obj_id = 'some_existing_object_id'
        obj = get_object(obj_id)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.type, 'blob')

if __name__ == '__main__':
    unittest.main()