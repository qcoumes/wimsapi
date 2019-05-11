import os
import unittest

from wimsapi.api import WimsAPI
from wimsapi.exceptions import AdmRawError, NotSavedError
from wimsapi.user import User
from wimsapi.wclass import Class


WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi"



class UserTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Create an API and an User to use through the tests."""
        cls.api = WimsAPI(WIMS_URL, "myself", "toto")
        cls.user = User("supervisor", "last", "first", "pass", "mail@mail.com")
        cls.clas = Class("myclass", "A class", "an institution", "mail@mail.com",
                         "password", cls.user, qclass=999999)
        cls.api.delclass(999999, "myclass")
    
    
    def tearDown(self):
        self.api.delclass(999999, "myclass")
        self.clas._saved = False
    
    
    def test_init_and_properties(self):
        c = Class.get(WIMS_URL, "myself", "toto", 9001, "myclass")
        u = User.get(c, "supervisor")
        self.assertIn("firstname", u.infos)
        
        u = User("supervisor", "last", "first", "pass", "mail@mail.com")
        self.assertEqual(u.fullname, "First Last")
        with self.assertRaises(NotSavedError):
            u.infos
    
    
    def test_get_exception(self):
        with self.assertRaises(NotSavedError):
            User.get(self.clas, "supervisor")
        
        self.clas.save(WIMS_URL, "myself", "toto")
        with self.assertRaises(AdmRawError) as cm:
            User.get(self.clas, "unknown")
        self.assertIn("WIMS' server responded with an ERROR:", str(cm.exception))
    
    
    def test_save_and_refresh(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        u = User("Test", "test", "test", "pass", "mail@mail.com")
        
        with self.assertRaises(NotSavedError):
            u.refresh()
        
        u.save(self.clas)
        
        u2 = User.get(self.clas, u.quser)
        self.assertEqual(u2.firstname, "test")
        
        u.firstname = "modified"
        u.save()
        
        self.assertEqual(u.firstname, "modified")
        self.assertEqual(u2.firstname, "test")
        u2.refresh()
        self.assertEqual(u2.firstname, "modified")
    
    
    def test_check(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        u = User("Test", "test", "test", "pass", "mail@mail.com")
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        
        with self.assertRaises(NotSavedError):
            User.check(c, u)
        
        self.assertFalse(User.check(self.clas, u))
        self.clas.additem(u)
        self.assertTrue(User.check(self.clas, u))
    
    
    def test_save_exceptions(self):
        with self.assertRaises(NotSavedError):
            self.user.save()
        
        with self.assertRaises(NotSavedError):
            self.user.save(self.clas)
    
    
    def test_delete(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        u = User("Test", "test", "test", "pass", "mail@mail.com")
        
        with self.assertRaises(NotSavedError):
            u.delete()
        
        u.save(self.clas)
        User.get(self.clas, u.quser)  # Ok
        u.delete()
        with self.assertRaises(AdmRawError):
            User.get(self.clas, u.quser)  # Should raise the exception
    
    
    def test_remove(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        u = User("Test", "test", "test", "pass", "mail@mail.com")
        
        with self.assertRaises(NotSavedError):
            u.remove(c, u)
        
        u.save(self.clas)
        User.get(self.clas, u.quser)  # Ok
        User.remove(self.clas, u)
        with self.assertRaises(AdmRawError):
            User.get(self.clas, u.quser)  # Should raise the exception
    
    
    def test_list(self):
        u1 = User("Test1", "test", "test", "pass", "mail@mail.com")
        u2 = User("Test2", "test", "test", "pass", "mail@mail.com")
        u3 = User("Test3", "test", "test", "pass", "mail@mail.com")
        
        self.clas.save(WIMS_URL, "myself", "toto")
        self.clas.additem(u1)
        self.clas.additem(u2)
        self.clas.additem(u3)
        
        self.assertListEqual(
            sorted([u1, u2, u3], key=lambda i: i.quser),
            sorted(User.list(self.clas), key=lambda i: i.quser)
        )
    
    
    def test_eq(self):
        u1 = User("Test1", "test", "test", "pass", "mail@mail.com")
        u2 = User("Test2", "test", "test", "pass", "mail@mail.com")
        u3 = User("Test3", "test", "test", "pass", "mail@mail.com")
        
        self.clas.save(WIMS_URL, "myself", "toto")
        self.clas.additem(u1)
        self.clas.additem(u2)
        
        self.assertEqual(u1, self.clas.getitem(u1.quser, User))
        self.assertNotEqual(u2, self.clas.getitem(u1.quser, User))
        self.assertNotEqual(u2, 1)
        
        with self.assertRaises(NotSavedError):
            u1 == u3
