import unittest
import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from flowapp import db, bcrypt, mail
from flowapp.models import User


class TestAdd(unittest.TestCase):
    """
    Test the add function from the mymath library
    """

    def test_new_user(self):
        """
        GIVEN a User model
        WHEN a new User is created
        THEN check the email, hashed_password, authenticated, and role fields are defined correctly
        """

        new_user = User(username='leonardo', password=bcrypt.generate_password_hash(
            'flowapp').decode('utf-8'), active='S', rol='111')
        self.assertEqual(new_user.username, 'leonardo')
        self.assertEqual(bcrypt.check_password_hash(new_user.password, 'flowapp'), True)
        self.assertEqual(new_user.active, 'S')
        self.assertEqual(new_user.rol, '111')




if __name__ == '__main__':
    unittest.main()
