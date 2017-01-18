import os
from rasp_server import rasp_server
import unittest
import tempfile
import json
from mock import MagicMock, patch
import sqlite3

class Test_Users(unittest.TestCase):
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

    def test_user_creation(self):
        response = self.app.post("/user", data=dict(nickname="Test"))
        self.assertEqual(response.data, '1')
        
    def test_first_user_creation_is_super(self):
        creation_response = self.app.post("/user", data=dict(nickname="Test"))
        
        user_key = creation_response.data
        retrieve_response = self.app.get("/user/%s" % user_key)

        data = json.loads(retrieve_response.data)
        self.assertEqual(data["user_key"], 1)
        self.assertEqual(data["permissions"], "su")
        
    def test_second_user_creation_is_readonly(self):
        self.create_sample_data()

        response = self.app.get("/user/2")
        data = json.loads(response.data)

        self.assertEqual(data["permissions"], "r")

    @patch.object(rasp_server.User, 'create')
    def test_user_creation_database_exception(self, mock_create):
        mock_create.side_effect = sqlite3.Error("Error")

        response = self.app.post("/user", data=dict(nickname="Test"))

        self.assertEqual(response.status_code, 500)

    def test_user_creation_without_nickname(self):
        response = self.app.post("/user")

        self.assertEqual(response.status_code, 400)

    def test_user_retrieval(self):
        creation_response = self.app.post("/user", data=dict(nickname="Test"))

        if creation_response.status_code == 200:
            user_key = creation_response.data
            retrieve_response = self.app.get("/user/%s" % user_key)

            if retrieve_response.status_code == 200:
                data = json.loads(retrieve_response.data)
                self.assertEquals(data["user_key"], 1)
                self.assertEqual(data["nickname"], 'Test')
            else:
                self.fail("Retrieve expected 200 got %s" % retrieve_response.status_code)
        else:
            self.fail("Creation expected 200 got %s" % creation_response.status_code)

    def test_user_list(self):
        creation_response = self.app.post("/user", data=dict(nickname="Test"))

        if creation_response.status_code == 200:
            retrieve_response = self.app.get("/user")

            if retrieve_response.status_code == 200:
                data = json.loads(retrieve_response.data)
                self.assertEqual(data[0]["nickname"], "Test")
            else:
                self.fail("Retrieve expected 200 got %s" % retrieve_response.status_code)
        else:
            self.fail("Creation expected 200 got %s" % creation_response.status_code)
    
    def test_user_list_multiple(self):
        self.app.post("/user", data=dict(nickname="Test1"))
        self.app.post("/user", data=dict(nickname="Test2"))

        retrieve_response = self.app.get("/user")

        data = json.loads(retrieve_response.data)
        self.assertEqual(data[0]["nickname"], "Test1")
        self.assertEqual(data[1]["nickname"], "Test2")

    def test_user_list_with_no_users(self):
        retrieve_response = self.app.get("/user")

        data = json.loads(retrieve_response.data)
        self.assertEqual(data, [])
    
    def test_user_update(self):
        self.create_sample_data()
        update_response = self.app.put("/user/1", data=dict(nickname="Test3"))

        retrieve_response = self.app.get("/user/1")
        data = json.loads(retrieve_response.data)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(data["nickname"], "Test3")

    def test_user_update_does_not_effect_others(self):
        self.create_sample_data()
        self.app.put("/user/1", data=dict(nickname="Test3"))

        retrieve_response = self.app.get("/user/2")
        data = json.loads(retrieve_response.data)
        self.assertEqual(data["nickname"], "Test2")

    def test_user_update_without_nickname(self):
        self.create_sample_data()
        update_response = self.app.put("/user/1")

        self.assertEquals(update_response.status_code, 400)

    def test_user_sethome(self):
        self.app.post("/user", data=dict(nickname="Test"))
        self.app.post("/home", data=dict(name="Home", password="password"))

        set_home_response = self.app.put("/user/1/sethome", data=dict(password="password", home_id=1))

        retrieve_response = self.app.get("/user/1")

        data = json.loads(retrieve_response.data)

        self.assertEqual(set_home_response.status_code, 200)
        self.assertEqual(data["home"], "1")
    
    def test_user_sethome_password_incorrect(self):
        self.app.post("/user", data=dict(nickname="Test"))
        self.app.post("/home", data=dict(name="Home", password="password"))

        set_home_response = self.app.put("/user/1/sethome", data=dict(password="wrong", home_id=1))

        retrieve_response = self.app.get("/user/1")
        data = json.loads(retrieve_response.data)
        self.assertEqual(set_home_response.status_code, 400)
        self.assertEqual(data["home"], None)
    
    def test_user_sethome_nonexistent_user(self):
        self.app.put("/home", data=dict(name="home", password="password"))
        set_home_response = self.app.put("/user/1/sethome", data=dict(password="password", home_id=1))

        self.assertEqual(set_home_response.status_code, 404)

    def test_user_sethome_nonexistent_home(self):
        self.app.put("/user", data=dict(nickname="Test"))
        set_home_response = self.app.put("/user/1/sethome", data=dict(password="password", home_id=1))

        self.assertEqual(set_home_response.status_code, 400)

    def test_user_sethome_no_home_id(self):
        self.app.post("/user", data=dict(nickname="Test"))
        self.app.post("/home", data=dict(name="Home", password="password"))

        set_home_response = self.app.put("/user/1/sethome", data=dict(password="password"))

        self.assertEqual(set_home_response.status_code, 400)

    def test_user_sethome_no_password(self):
        self.app.post("/user", data=dict(nickname="Test"))
        self.app.post("/home", data=dict(name="Home", password="password"))

        set_home_response = self.app.put("/user/1/sethome", data=dict(home_id=1))

        self.assertEqual(set_home_response.status_code, 400)

    def test_user_sethome_no_password_or_id(self):
        self.app.post("/user", data=dict(nickname="Test"))
        self.app.post("/home", data=dict(name="Home", password="password"))

        set_home_response = self.app.put("/user/1/sethome")

        self.assertEqual(set_home_response.status_code, 400)
if __name__ == '__main__':
    unittest.main()