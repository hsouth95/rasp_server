import os
from rasp_server import rasp_server
import unittest
import tempfile
import json
from mock import MagicMock, patch
import sqlite3

class Test_Rotations(unittest.TestCase):
    def setUp(self):
        self.db_fd, rasp_server.app.config["DATABASE"] = tempfile.mkstemp()
        rasp_server.app.config["TESTING"] = True
        self.app = rasp_server.app.test_client()
        with rasp_server.app.app_context():
            rasp_server.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(rasp_server.app.config["DATABASE"])

    def test_create_rotation(self):

    def test_create_rotation_without_name(self):

    def test_get_rotation(self):

    def test_get_rotation_doesnt_exist(self):

if __name__ == '__main__':
    unittest.main()