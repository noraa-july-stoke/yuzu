#  ╦╔═┌─┐┬ ┬╦  ┬┌┬┐┌─┐
#  ╠╩╗├┤ └┬┘║  ││││├┤
#  ╩ ╩└─┘ ┴ ╩═╝┴┴ ┴└─┘
# File: key_lime.py
# Description: This file contains the KeyLime class which is used to store the
# keychain and encrypt and decrypt messages.
import os
from cryptography.fernet import Fernet

from typing import Dict

class KeyLime:
    def __init__(self, keychain: Dict[str, bytes] = {}):
        self.keychain = keychain

    def add_key(self, key_name: str, key: bytes):
        self.keychain[key_name] = key

    def remove_key(self, key_name: str):
        if key_name in self.keychain:
            del self.keychain[key_name]

    def get_key(self, key_name: str) -> bytes:
        return self.keychain.get(key_name)

    def encrypt(self, key_name: str, message: str) -> str:
        key = self.get_key(key_name)
        if key is not None:
            cipher_suite = Fernet(key)
            cipher_text = cipher_suite.encrypt(message.encode())
            return cipher_text.decode()  # Convert bytes to string
        else:
            raise ValueError("Invalid key")

    def decrypt(self, key_name: str, cipher_text: str) -> str:
        key = self.get_key(key_name)
        if key is not None:
            cipher_suite = Fernet(key)
            decoded_text = cipher_suite.decrypt(cipher_text.encode())
            return decoded_text.decode()  # Convert bytes to string
        else:
            raise ValueError("Invalid key")
