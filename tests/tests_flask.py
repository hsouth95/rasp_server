import os
import rasp_server
import unittest
import pprint
from mock import MagicMock, patch

class Test_rasp_server(unittest.TestCase):
	def setUp(self):
		rasp_server.app.get_file_contents = MagicMock(return_value="value")
		self.app = rasp_server.app.test_client()

	def test_hello_request_returns_value(self):
		response = self.app.get("/hello")
		self.assertEqual(response.status_code, 200)
	
	def test_user_request_exists(self):
		response = self.app.get("/user")
		self.assertNotEqual(response.status_code, 404)

	def test_get_user_no_key_returns_key(self):
		response = self.app.get("/user")
		self.assertTrue(isinstance(response.data, basestring))
		self.assertNotEqual(response.data, "")

	def test_get_user_exists(self):
		response = self.app.get("/user/randomvalue")
		self.assertNotEqual(response.status_code, 404)

	@patch.object(rasp_server.rasp_server, 'get_file_contents')
	def test_get_user_with_valid_key_returns_value(self, mock_get_file_contents):
		mock_get_file_contents.return_value = "value"

		response = self.app.get("/user/randomvalue")
		self.assertEqual(response.data, "value")
		
if __name__ == '__main__':
    unittest.main()
