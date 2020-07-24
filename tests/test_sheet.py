import os
import subprocess
import unittest

from wimsapi import ExerciseScore, SheetScore
from wimsapi.api import WimsAPI
from wimsapi.exceptions import AdmRawError, NotSavedError
from wimsapi.sheet import Sheet
from wimsapi.user import User
from wimsapi.utils import default
from wimsapi.wclass import Class


WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi/"



def command(cmd):
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    out, err = p.communicate()
    if p.returncode:
        raise RuntimeError(
            "Return code : " + str(p.returncode) + " - " + err.decode() + out.decode())
    return p.returncode, out.decode().strip(), err.decode()



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
    
    
    def test_default(self):
        d = {
            "a": [1, 2]
        }
        self.assertEqual(default(d, "a", 0), 1)
        self.assertEqual(default(d, "a", 1), 2)
        self.assertEqual(default(d, "a", 3), None)
        self.assertEqual(default(d, "a", 3, -1), -1)
        self.assertEqual(default(d, "b", 1), None)
        self.assertEqual(default(d, "b", 1, -1), -1)
    
    
    def test_compute_grade(self):
        formula = ("max(I,Q)", "I", "I*Q^0.3", "I*Q^0.5", "I*Q", "I^2*Q", "(I*Q)^2")
        I = (0, 1, 2)
        Q = 3.3
        cumul = best = acquired = 100
        expected = {
            formula[0]: {0: 10, 1: 10, 2: 10},
            formula[1]: {0: 10, 1: 10, 2: 10},
            formula[2]: {0: 7.17, 1: 7.17, 2: 7.17},
            formula[3]: {0: 5.74, 1: 5.74, 2: 5.74},
            formula[4]: {0: 3.3, 1: 3.3, 2: 3.3},
            formula[5]: {0: 3.3, 1: 3.3, 2: 3.3},
            formula[6]: {0: 1.09, 1: 1.09, 2: 1.09},
        }
        for f in formula:
            for i in I:
                self.assertEqual(
                    Sheet._compute_grade(f, i, Q, cumul, best, acquired),
                    expected[f][i]
                )
    
    
    def test_scores(self):
        # Put a dummy class with existing scores if not already added
        qclass = 6948902
        if not Class.check(self.api.url, self.api.ident, self.api.passwd, qclass, "myclass"):
            archive = os.path.join(os.path.dirname(__file__), "resources/6948902.tgz")
            command("docker cp %s wims-minimal:/home/wims/log/classes/" % archive)
            command('docker exec wims-minimal bash -c '
                    '"tar -xzf /home/wims/log/classes/6948902.tgz -C /home/wims/log/classes/"'
                    )
            command(
                'docker exec wims-minimal bash -c "chmod 644 /home/wims/log/classes/6948902/.def"'
            )
            command(
                'docker exec wims-minimal bash -c '
                '"chown wims:wims /home/wims/log/classes/6948902 -R"'
            )
            command('docker exec wims-minimal bash -c "rm /home/wims/log/classes/6948902.tgz"')
            command(
                "docker exec wims-minimal bash -c "
                "\"echo ':6948902,20200626,Institution,test,en,0,H4,dmi,S S,+myself/myclass+,' "
                '>> /home/wims/log/classes/.index"'
            )
        
        with self.assertRaises(NotSavedError):
            Sheet().scores()
        
        c = Class.get(self.api.url, self.api.ident, self.api.passwd, qclass, "myclass")
        s1 = c.getitem(1, Sheet)
        s2 = c.getitem(2, Sheet)
        u = c.getitem("qcoumes", User)
        
        es1_1 = ExerciseScore(None, u, 3.3, 10, 10, 10, 0, 10, 1, 3)
        ss1 = SheetScore(s1, u, 7.17, 3.3, 100, 100, 100, 1, [es1_1])
        
        es2_1 = ExerciseScore(None, u, 4.59, 10, 10, 10, 0, 10, 1, 2)
        es2_2 = ExerciseScore(None, u, 5.41, 10, 10, 10, 10, 10, 1, 2)
        ss2 = SheetScore(s2, u, 8.12, 5, 100, 100, 100, 1, [es2_1, es2_2])
        
        self.assertEqual(s1.scores("qcoumes"), ss1)
        self.assertEqual(s1.scores(), [ss1])
        self.assertEqual(s2.scores("qcoumes"), ss2)
        self.assertEqual(s2.scores(), [ss2])
        
        with self.assertRaises(ValueError):
            s1.scores("unknown")
