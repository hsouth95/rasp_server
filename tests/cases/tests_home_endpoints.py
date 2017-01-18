import os
from rasp_server import rasp_server
import unittest
import tempfile
import json
from mock import MagicMock, patch
import sqlite3

class Test_Homes(unittest.TestCase):
    def setUp(self):
        self.db_fd, rasp_server.app.config["DATABASE"] = tempfile.mkstemp()
        rasp_server.app.config["TESTING"] = True
        self.app = rasp_server.app.test_client()
        with rasp_server.app.app_context():
            rasp_server.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(rasp_server.app.config["DATABASE"])

    def test_create_home(self):
        create_response = self.app.post("/home", data=dict(name="Test", password="password"))
        retrieve_response = self.app.get("/home/1")
        data = json.loads(retrieve_response.data)

        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(create_response.data, "1")
        self.assertEqual(data["name"], "Test")
    
    def test_create_home_without_password(self):
        create_response = self.app.post("/home", data=dict(name="Test"))

        self.assertEqual(create_response.status_code, 400)
    
    def test_create_home_without_name(self):
        create_response = self.app.post("/home", data=dict(password="password"))

        self.assertEqual(create_response.status_code, 400)

    def test_get_home(self):
        self.app.post("/home", data=dict(name="Test", password="password"))

        retrieve_response = self.app.get("/home/1")
        data = json.loads(retrieve_response.data)

        self.assertEqual(retrieve_response.status_code, 200)
        self.assertEqual(data["name"], "Test")
        self.assertEqual(data["id"], 1) 
        
    def test_get_home_not_exists(self):
        retrieve_response = self.app.get("/home/1")

        self.assertEqual(retrieve_response.status_code, 404)

    def test_list_home(self):
        self.app.post("/home", data=dict(name="Test", password="password"))
        retrieve_response = self.app.get("/home")

        data = json.loads(retrieve_response.data)

        self.assertEqual(retrieve_response.status_code, 200)
        self.assertEqual(data[0]["name"], "Test")
    
    def test_list_multiple(self):
        self.app.post("/home", data=dict(name="Test", password="password"))
        self.app.post("/home", data=dict(name="Test2", password="password"))
        retrieve_response = self.app.get("/home")

        data = json.loads(retrieve_response.data)

        self.assertEqual(retrieve_response.status_code, 200)
        self.assertEqual(data[0]["name"], "Test")
        self.assertEqual(data[1]["name"], "Test2")
    
    def test_list_no_homes(self):
        retrieve_response = self.app.get("/home")
        data = json.loads(retrieve_response.data)

        self.assertEqual(retrieve_response.status_code, 200)
        self.assertEqual(data, [])

    def test_update_home(self):
        self.app.post("/home", data=dict(name="Test", password="password"))

        update_response = self.app.put("/home/1", data=dict(name="Test1"))
        retrieve_response = self.app.get("/home/1")
        data = json.loads(retrieve_response.data)

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(data["name"], "Test1")
    
    def test_update_home_without_name(self):
        self.app.post("/home", data=dict(name="Test", password="password"))

        update_response = self.app.put("/home/1")

        self.assertEqual(update_response.status_code, 400)

    def test_update_does_not_effect_others(self):
        self.app.post("/home", data=dict(name="Test", password="password"))
        self.app.post("/home", data=dict(name="Test1", password="password"))

        self.app.put("/home/1", data=dict(name="Test2"))

        retrieve_response = self.app.get("/home/2")
        data = json.loads(retrieve_response.data)

        self.assertEqual(data["name"], "Test1")
        
if __name__ == '__main__':
    unittest.main()