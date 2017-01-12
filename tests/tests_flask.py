import os
from rasp_server import rasp_server
import unittest
import tempfile
import json
from mock import MagicMock, patch


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

    def test_hello_request_returns_value(self):
        response = self.app.get("/hello")
        self.assertEqual(response.status_code, 200)

    def test_empty_db(self):
        response = self.app.get("/user/randomvalue")
        self.assertEqual(response.status_code, 404)

    def test_user_key_creation(self):
        response = self.app.post("/user", data=dict(nickname="Test"))
        self.assertEqual(response.data, '1')

    @patch.object(rasp_server.User, 'create')
    def test_user_key_creation_database_exception(self, mock_create):
        mock_create.side_effect = Exception("Error")

        response = self.app.post("/user", data=dict(nickname="Test"))

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data, "Error creating User")

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

if __name__ == '__main__':
    unittest.main()
