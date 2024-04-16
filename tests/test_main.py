import unittest
import hashlib
import logging
import os
import secrets
import string
import threading
from datetime import datetime
import pandas as pd

import data_generator

class TestUserManagement(unittest.TestCase):
    def setUp(self):
        """
        Set up test fixtures.

        This method is called before each test method is executed.
        """
        self.test_db_name = 'test_users.db'
        self.test_username = 'test_user'
        self.test_password = 'test_password'
        self.test_salt = secrets.token_hex(8)
        self.test_hashed_password = hashlib.sha256((self.test_password + self.test_salt).encode()).hexdigest()
        self.test_hashed_password_with_salt = f"{self.test_hashed_password}:{self.test_salt}"

    def tearDown(self):
        """
        Clean up test fixtures.

        This method is called after each test method is executed.
        """
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)

    def test_constructor(self):
        """
        Test the constructor of the UserManagement class.
        """
        user_manager = UserManagement(self.test_db_name)
        self.assertEqual(user_manager.db_name, self.test_db_name)

    def test_create_table(self):
        """
        Test the create_table method of the UserManagement class.
        """
        user_manager = UserManagement(self.test_db_name)
        user_manager.create_table()
        self.assertTrue(os.path.exists(self.test_db_name))

    def test_register(self):
        """
        Test the register method of the UserManagement class.
        """
        user_manager = UserManagement(self.test_db_name)
        user_manager.create_table()
        registered = user_manager.register(self.test_username, self.test_password)
        self.assertTrue(registered)
        # Attempt to register the same user again
        registered = user_manager.register(self.test_username, self.test_password)
        self.assertFalse(registered)

    def test_login(self):
        """
        Test the login method of the UserManagement class.
        """
        user_manager = UserManagement(self.test_db_name)
        user_manager.create_table()
        user_manager.register(self.test_username, self.test_password)
        logged_in = user_manager.login(self.test_username, self.test_password)
        self.assertTrue(logged_in)
        logged_in = user_manager.login(self.test_username, 'wrong_password')
        self.assertFalse(logged_in)

    def test_reset_password(self):
        """
        Test the reset_password method of the UserManagement class.
        """
        user_manager = UserManagement(self.test_db_name)
        user_manager.create_table()
        user_manager.register(self.test_username, self.test_password)
        reset = user_manager.reset_password(self.test_username)
        self.assertTrue(reset)
        # Attempt to reset password of a non-existent user
        reset = user_manager.reset_password('non_existent_user')
        self.assertFalse(reset)

    def test_hash_password(self):
        """
        Test the hash_password method of the UserManagement class.
        """
        user_manager = UserManagement()
        hashed_password = user_manager.hash_password(self.test_password, self.test_salt)
        self.assertEqual(hashed_password, self.test_hashed_password)


if __name__ == '__main__':
    unittest.main()


