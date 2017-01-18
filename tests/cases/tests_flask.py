import os
from rasp_server import rasp_server
import unittest
import tempfile
import json
from mock import MagicMock, patch
import sqlite3


class Test_rasp_server(unittest.TestCase):
    def setUp(self):
        self.db_fd, rasp_server.app.config["DATABASE"] = tempfile.mkstemp()
        rasp_server.app.config["TESTING"] = True
        self.app = rasp_server.app.test_client()
        with rasp_server.app.app_context():
            rasp_server.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(rasp_server.app.config["DATABASE"])
    
    def create_sample_data(self):
        self.app.post("/user", data=dict(nickname="Test"))
        self.app.post("/user", data=dict(nickname="Test2"))

    def test_hello_request_returns_value(self):
        response = self.app.get("/hello")
        self.assertEqual(response.status_code, 200)

    def test_empty_db(self):
        response = self.app.get("/user/randomvalue")
        self.assertEqual(response.status_code, 404)
        
if __name__ == '__main__':
    unittest.main()
