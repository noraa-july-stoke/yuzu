import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import bcrypt
from cryptography.fernet import Fernet
from flask import g, Flask, jsonify
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tangerine_auth import KeyLime, Yuzu



class TestYuzu(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Mock methods
        cls.get_user_by_email = MagicMock(return_value={
                                          "email": "test@example.com", "password": bcrypt.hashpw('password'.encode(), bcrypt.gensalt()).decode()})
        cls.create_user = MagicMock()

        cls.key_lime = KeyLime()
        cls.key_name = "SECRET_KEY"
        cls.key = Fernet.generate_key()
        cls.key_lime.add_key(cls.key_name, cls.key)

    def setUp(self):
        self.yuzu = Yuzu(
            self.key_lime, self.get_user_by_email, self.create_user)

    def test_authenticate(self):
        print("Running test_authenticate")
        self.assertTrue(self.yuzu.authenticate("test@example.com", "password"))
        self.assertFalse(self.yuzu.authenticate(
            "test@example.com", "wrong_password"))

    def test_generate_auth_token(self):
        print("Running test_generate_auth_token")
        token = self.yuzu.generate_auth_token('123', 'test@example.com')
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_verify_auth_token(self):
        print("Running test_verify_auth_token")
        token = self.yuzu.generate_auth_token('123', 'test@example.com')
        decoded_token = self.yuzu.verify_auth_token(token)
        self.assertEqual(decoded_token['user_id'], '123')
        self.assertEqual(decoded_token['email'], 'test@example.com')

    def test_jwt_middleware(self):
        print("Running test_jwt_middleware")
        ctx = MagicMock()
        ctx.get_req_header = MagicMock(
            return_value=self.yuzu.generate_auth_token('123', 'test@example.com'))

        next_func = MagicMock()
        self.yuzu.jwt_middleware(ctx, next_func)

        self.assertTrue(ctx.auth)
        self.assertEqual(ctx.user['user_id'], '123')

    def test_sign_up(self):
        print("Running test_sign_up")
        user_data = {"email": "newuser@example.com", "password": "password"}
        self.create_user.return_value = user_data

        result = self.yuzu.sign_up(user_data)
        self.assertEqual(result, user_data)

    def test_login(self):
        print("Running test_login")
        user_id, token = self.yuzu.login("test@example.com", "password")
        self.assertIsNotNone(user_id)
        self.assertIsNotNone(token)

        user_id, token = self.yuzu.login("test@example.com", "wrong_password")
        self.assertIsNone(user_id)
        self.assertIsNone(token)

    def test_logout(self):
        print("Running test_logout")
        ctx = MagicMock()
        self.yuzu.auth = True
        self.yuzu.logout(ctx)

        self.assertFalse(self.yuzu.auth)
        self.assertIsNone(ctx.user)



    def test_flask_jwt_middleware(self):
        # Set up mock objects
        mock_token = 'mock_token'
        mock_user = {'user_id': '123', 'email': 'test@example.com'}
        yuzu_instance = Yuzu(..., get_user_by_email=lambda: {"id": 123, "email": "mtest@test.com", "password": "test"}, create_user=lambda: {"id": 123, "email": "mtest@test.com", "password": "test"})
        yuzu_instance.verify_auth_token = MagicMock(return_value=mock_user)

        # Define a mock Flask app for testing
        app = Flask(__name__)

        # Create a test client
        client = app.test_client()

        # Define a route for testing
        @app.route('/')
        def test_route():
            if g.user:
                print("User exists:", g.user)
                return jsonify({'success': True, 'user_id': g.user['user_id'], 'email': g.user['email']})
            else:
                print("User does not exist")
                return jsonify({'success': False, 'message': 'Unauthorized'})

        # Apply the middleware decorator
        @yuzu_instance.flask_jwt_middleware()
        def mock_func():
            print("Invoked mock_func")
            return True

        # Set the user in the global context (g)
        with app.app_context():
            # Set user to None to simulate no user
            g.user = None

            # Invoke the decorated function
            with client:
                print("Sending request with no user")
                response = client.get('/', headers={'Authorization': mock_token})
                result = mock_func()

            # Assertions for no user (Unauthorized)
            print("Assertions for no user (Unauthorized)")
            self.assertTrue(result)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json(), {'success': False, 'message': 'Unauthorized'})
            yuzu_instance.verify_auth_token.assert_called_with(mock_token)

            # Set user to the mock user to simulate a valid user
            g.user = mock_user

            # Invoke the decorated function again
            with client:
                print("Sending request with valid user")
                response = client.get('/', headers={'Authorization': mock_token})
                result = mock_func()

            # Assertions for valid user
            print("Assertions for valid user")
            self.assertTrue(result)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json(), {'success': True, 'user_id': '123', 'email': 'test@example.com'})
            yuzu_instance.verify_auth_token.assert_called_with(mock_token)




if __name__ == "__main__":
    unittest.main()
