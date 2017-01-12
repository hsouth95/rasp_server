import os
import rasp_server
import unittest
import tempfile
import pprint
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

    # @patch.object(rasp_server.rasp_server, 'get_file_contents')
    # def test_get_user_with_valid_key_returns_value(self, mock_get_file_contents):
    #     mock_get_file_contents.return_value = "value"
    #
    #     response = self.app.get("/user/randomvalue")
    #     self.assertEqual(response.data, "value")

if __name__ == '__main__':
    unittest.main()
