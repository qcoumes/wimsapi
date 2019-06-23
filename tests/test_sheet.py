import os
import unittest

from wimsapi.api import WimsAPI
from wimsapi.exceptions import AdmRawError, NotSavedError
from wimsapi.sheet import Sheet
from wimsapi.user import User
from wimsapi.wclass import Class


WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi"



class SheetTestCase(unittest.TestCase):
    
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
        s = Sheet("Title", "Description")
        self.assertEqual(s.exo_count, 0)
        self.assertRaises(NotSavedError, lambda: s.infos)
        self.clas.save(WIMS_URL, "myself", "toto")
        self.clas.additem(s)
        self.assertIn("sheet_title", s.infos)
    
    
    def test_get_exception(self):
        with self.assertRaises(NotSavedError):
            Sheet.get(self.clas, 1)
        
        self.clas.save(WIMS_URL, "myself", "toto")
        with self.assertRaises(AdmRawError) as cm:
            Sheet.get(self.clas, 50)
        self.assertIn("WIMS' server responded with an ERROR:", str(cm.exception))
    
    
    def test_save_and_refresh(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        s = Sheet("Title", "Description")
        
        with self.assertRaises(NotSavedError):
            s.refresh()
        
        s.save(self.clas)
        
        s2 = Sheet.get(self.clas, s.qsheet)
        self.assertEqual(s2.title, "Title")
        
        s.title = "modified"
        s.save()
        
        self.assertEqual(s.title, "modified")
        self.assertEqual(s2.title, "Title")
        s2.refresh()
        self.assertEqual(s2.title, "modified")
    
    
    def test_check(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        s = Sheet("Title", "Description")
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        
        with self.assertRaises(NotSavedError):
            Sheet.check(c, s)
        
        self.assertFalse(Sheet.check(self.clas, s))
        self.clas.additem(s)
        self.assertTrue(Sheet.check(self.clas, s))
    
    
    def test_save_exceptions(self):
        s = Sheet("Title", "Description")
        with self.assertRaises(NotSavedError):
            s.save()
        
        with self.assertRaises(NotSavedError):
            s.save(self.clas)
    
    
    def test_delete(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        s = Sheet("Title", "Description")
        
        with self.assertRaises(NotSavedError):
            s.delete()
        
        s.save(self.clas)
        Sheet.get(self.clas, s.qsheet)  # Ok
        s.delete()
        with self.assertRaises(AdmRawError):
            Sheet.get(self.clas, s.qsheet)  # Should raise the exception
    
    
    def test_remove(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        s = Sheet("Title", "Description")
        
        with self.assertRaises(NotSavedError):
            s.remove(c, s)
        
        s.save(self.clas)
        Sheet.get(self.clas, s.qsheet)  # Ok
        Sheet.remove(self.clas, s)
        with self.assertRaises(AdmRawError):
            Sheet.get(self.clas, s.qsheet)  # Should raise the exception
    
    
    def test_list(self):
        s1 = Sheet("First", "First one")
        s2 = Sheet("Second", "Second one")
        s3 = Sheet("Third", "Third one")
        
        self.clas.save(WIMS_URL, "myself", "toto")

        self.assertListEqual(
            [],
            Sheet.list(self.clas)
        )
        
        self.clas.additem(s1)
        self.clas.additem(s2)
        self.clas.additem(s3)
        
        self.assertListEqual(
            sorted([s1, s2, s3], key=lambda i: i.qsheet),
            sorted(Sheet.list(self.clas), key=lambda i: i.qsheet)
        )
    
    
    def test_eq(self):
        s1 = Sheet("First", "First one")
        s2 = Sheet("Second", "Second one")
        s3 = Sheet("Third", "Third one")
        
        self.clas.save(WIMS_URL, "myself", "toto")
        self.clas.additem(s1)
        self.clas.additem(s2)
        
        self.assertEqual(s1, self.clas.getitem(s1.qsheet, Sheet))
        self.assertNotEqual(s2, self.clas.getitem(s1.qsheet, Sheet))
        self.assertNotEqual(s2, 1)
        
        self.assertRaises(NotSavedError, lambda: s1 == s3)
