import datetime
import unittest
from unittest import mock

from wimsapi.user import User
from wimsapi.wclass import Class, one_year_later
from wimsapi.api import WimsAPI
from wimsapi.exceptions import AdmRawException


WIMS_URL = "http://localhost:7777/wims/wims.cgi"



class FakeDate(datetime.date):
    """Used to override datetime.date.today"""
    
    
    @classmethod
    def today(cls):
        """Always return a Date corresponding to 1966-11-16."""
        return datetime.date(1966, 11, 16)



class ClassTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Create an API and an User to use through the tests."""
        cls.api = WimsAPI(WIMS_URL, "myself", "toto")
        cls.user = User("supervisor", "last", "first", "pass", "mail@mail.com")
    
    
    def tearDown(self):
        """Delete classes that a test might have created."""
        self.api.delclass(999999, "myclass")
        self.api.delclass(999666, "myclass")
        self.api.delclass(999990, "myclass")
    
    
    @mock.patch('datetime.date', FakeDate)
    def test_one_year_later(self):
        self.assertEqual(one_year_later(), "19671116")
    
    
    def test_init_and_properties(self):
        c = Class.get(WIMS_URL, "myself", "toto", 9001, "myclass")
        self.assertEqual(c.url, WIMS_URL)
        self.assertEqual(c.ident, "myself")
        self.assertEqual(c.passwd, "toto")
        self.assertIn("description", c.infos)
        
        c = Class(999999, "myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user)
        with self.assertRaises(ValueError):
            c.url
        with self.assertRaises(ValueError):
            c.ident
        with self.assertRaises(ValueError):
            c.passwd
        with self.assertRaises(ValueError):
            c.infos
        
        with self.assertRaises(ValueError):
            Class(999999, "myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, lang="Wrong")
        with self.assertRaises(ValueError):
            Class(999999, "myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, level="Wrong")
        with self.assertRaises(ValueError):
            Class(999999, "myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, date="Wrong")
    
    
    def test_save_and_refresh(self):
        c = Class(999999, "myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user)
        
        with self.assertRaises(ValueError):
            c.save()
        
        with self.assertRaises(ValueError):
            c.refresh()
        
        c.save(WIMS_URL, "myself", "toto")
        c = Class.get(WIMS_URL, "myself", "toto", 999999, "myclass")
        c2 = Class.get(WIMS_URL, "myself", "toto", 999999, "myclass")
        
        self.assertEqual(c.institution, "an institution")
        self.assertEqual(c2.institution, "an institution")
        
        c.institution = "modified"
        c.save()
        self.assertEqual(c.institution, "modified")
        self.assertEqual(c2.institution, "an institution")
        
        c2.refresh()
        self.assertEqual(c2.institution, "modified")
        self.api.delclass(99999999, "myclass")
    
    
    def test_get_user(self):
        c = Class(999999, "myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user)
        
        with self.assertRaises(ValueError):
            c.get_user("supervisor")
        
        c.save(WIMS_URL, "myself", "toto")
        user = c.get_user("supervisor")
        self.assertEqual(user.firstname, self.user.firstname)
    
    
    def test_add_user(self):
        c = Class(999999, "myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user)
        u = User("quser", "last", "first", "pass", "mail2@mail.com")
        
        with self.assertRaises(ValueError):
            c.add_user(u)
        
        c.save(WIMS_URL, "myself", "toto")
        c.add_user(u)
        self.assertEqual(u._class.qclass, c.qclass)
        self.assertEqual(u._saved, True)
        
        u2 = c.get_user("test")
        self.assertEqual(u2.firstname, u.firstname)
    
    
    def test_delete(self):
        c = Class(999999, "myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user)
        
        with self.assertRaises(ValueError):
            c.delete()
        
        c.save(WIMS_URL, "myself", "toto")
        
        Class.get(WIMS_URL, "myself", "toto", c.qclass, c.rclass)  #  Ok
        c.delete()
        with self.assertRaises(AdmRawException):
            Class.get(WIMS_URL, "myself", "toto", c.qclass, c.rclass)  # Should raise the exception
