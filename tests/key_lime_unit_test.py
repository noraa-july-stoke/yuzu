import sys
import os
import unittest
from unittest.mock import MagicMock
from cryptography.fernet import Fernet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tangerine_auth.key_lime import KeyLime

class TestKeyLime(unittest.TestCase):

    def test_add_key(self):
        print("Running test_add_key")
        key_lime = KeyLime()
        key_name = "test_key"
        key = b'secret-key'
        key_lime.add_key(key_name, key)
        self.assertEqual(key_lime.get_key(key_name), key)

    def test_remove_key(self):
        print("Running test_remove_key")
        key_lime = KeyLime()
        key_name = "test_key"
        key = b'secret-key'
        key_lime.add_key(key_name, key)
        key_lime.remove_key(key_name)
        self.assertIsNone(key_lime.get_key(key_name))

    def test_encrypt_decrypt(self):
        print("Running test_encrypt_decrypt")
        key_lime = KeyLime()
        key_name = "test_key"
        key = Fernet.generate_key()
        key_lime.add_key(key_name, key)
        message = "Hello, World!"
        cipher_text = key_lime.encrypt(key_name, message)
        decrypted_text = key_lime.decrypt(key_name, cipher_text)
        self.assertEqual(message, decrypted_text)

if __name__ == "__main__":
    unittest.main()
