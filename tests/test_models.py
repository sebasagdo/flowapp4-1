import unittest
import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from flowapp import db, bcrypt, mail
from flowapp.models import User, Device, Categoria,Unit


class UserAdd(unittest.TestCase):


    def test_new_user(self):


        new_user = User(username='leonardo', password=bcrypt.generate_password_hash(
            'flowapp').decode('utf-8'), active='S', rol='111')
        self.assertEqual(new_user.username, 'leonardo')
        self.assertEqual(bcrypt.check_password_hash(new_user.password, 'flowapp'), True)
        self.assertEqual(new_user.active, 'S')
        self.assertEqual(new_user.rol, '111')

class DeviceAdd(unittest.TestCase):

    def test_new_device(self):

        new_device = Device(id=1,serialID='2121')
        self.assertEqual(new_device.id, 1)
        self.assertEqual(new_device.serialID, '2121')

class CategoryAdd(unittest.TestCase):

    def test_new_category(self):

        new_category = Categoria(id=1,title='Cocina')
        self.assertEqual(new_category.id, 1)
        self.assertEqual(new_category.title, 'Cocina')

class UnitAdd(unittest.TestCase):

    def test_new_unit(self):

        new_unit = Unit(id=1,name='Centimetros Cubicos')
        self.assertEqual(new_unit.id, 1)
        self.assertEqual(new_unit.name, 'Centimetros Cubicos')

if __name__ == '__main__':
    unittest.main()
