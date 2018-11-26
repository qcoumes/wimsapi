import unittest

from wimsapi.api import WimsAPI
from wimsapi.user import User
from wimsapi.wclass import Class
from wimsapi.exceptions import AdmRawError, NotSavedError

WIMS_URL = "http://localhost:7777/wims/wims.cgi"



class UserTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Create an API and an User to use through the tests."""
        cls.api = WimsAPI(WIMS_URL, "myself", "toto")
        cls.user = User("supervisor", "last", "first", "pass", "mail@mail.com")
        cls.clas = Class(999999, "myclass", "A class", "an institution", "mail@mail.com",
                         "password", cls.user)
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
