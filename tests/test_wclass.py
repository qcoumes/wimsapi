import datetime
import os
import unittest
from unittest import mock

from wimsapi.user import User
from wimsapi.wclass import Class, one_year_later
from wimsapi.api import WimsAPI
from wimsapi.exceptions import AdmRawError, NotSavedError, InvalidItemTypeError


WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi"



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
        
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        with self.assertRaises(NotSavedError):
            c.url
        with self.assertRaises(NotSavedError):
            c.ident
        with self.assertRaises(NotSavedError):
            c.passwd
        with self.assertRaises(NotSavedError):
            c.infos
        
        with self.assertRaises(ValueError):
            Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999, lang="Wrong")
        with self.assertRaises(ValueError):
            Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999, level="Wrong")
        with self.assertRaises(ValueError):
            Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999, date="Wrong")
    
    
    def test_save_and_refresh(self):
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        
        with self.assertRaises(NotSavedError):
            c.save()
        
        with self.assertRaises(NotSavedError):
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
    
    def test_save_without_qclass(self):
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user)
        
        with self.assertRaises(NotSavedError):
            c.save()
        
        c.save(WIMS_URL, "myself", "toto")
        self.assertIsNotNone(c.qclass)
        c.delete()
    
    
    def test_getitem(self):
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        
        with self.assertRaises(NotSavedError):
            c.getitem("supervisor", User)
        with self.assertRaises(InvalidItemTypeError):
            c.getitem(1, int)
        
        c.save(WIMS_URL, "myself", "toto")
        user = c.getitem("supervisor", User)
        self.assertEqual(user.firstname, self.user.firstname)
    
    
    def test_checkitem(self):
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        unknown = User("unknown", "last", "first", "pass", "mail2@mail.com")
        
        with self.assertRaises(NotSavedError):
            c.checkitem("supervisor", User)
        with self.assertRaises(InvalidItemTypeError):
            c.checkitem(1)
        
        c.save(WIMS_URL, "myself", "toto")
        self.assertTrue(c.checkitem("supervisor", User))
        self.assertTrue(c.checkitem(self.user))
        self.assertFalse(c.checkitem("Unknown", User))
        self.assertFalse(c.checkitem(unknown))
    
    
    def test___contains__(self):
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        unknown = User("unknown", "last", "first", "pass", "mail2@mail.com")
        
        with self.assertRaises(NotSavedError):
            unknown in c
        
        c.save(WIMS_URL, "myself", "toto")
        self.assertTrue(self.user in c)
        self.assertFalse(unknown in c)
    
    
    def test_additem(self):
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        u = User("quser", "last", "first", "pass", "mail2@mail.com")
        
        with self.assertRaises(NotSavedError):
            c.additem(u)
        with self.assertRaises(InvalidItemTypeError):
            c.additem(int)
        
        c.save(WIMS_URL, "myself", "toto")
        c.additem(u)
        self.assertEqual(u._class.qclass, c.qclass)
        self.assertEqual(u.wclass, True)
        
        u2 = c.getitem("quser", User)
        self.assertEqual(u2.firstname, u.firstname)
    
    
    def test_delitem(self):
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        u = User("quser", "last", "first", "pass", "mail2@mail.com")
        u2 = User("quser2", "last", "first", "pass", "mail2@mail.com")
        
        with self.assertRaises(NotSavedError):
            c.delitem(u)
        with self.assertRaises(InvalidItemTypeError):
            c.delitem(int)
        
        c.save(WIMS_URL, "myself", "toto")
        c.additem(u)
        c.additem(u2)
        
        self.assertTrue(c.checkitem("quser", User))
        c.delitem(u)
        self.assertFalse(c.checkitem("quser", User))
        
        self.assertTrue(c.checkitem("quser2", User))
        c.delitem("quser2", User)
        self.assertFalse(c.checkitem("quser2", User))
    
    
    def test_delete(self):
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        
        with self.assertRaises(NotSavedError):
            c.delete()
        
        c.save(WIMS_URL, "myself", "toto")
        
        Class.get(WIMS_URL, "myself", "toto", c.qclass, c.rclass)  #  Ok
        c.delete()
        with self.assertRaises(AdmRawError):
            Class.get(WIMS_URL, "myself", "toto", c.qclass, c.rclass)  # Should raise the exception
