import os
import subprocess
import unittest

from wimsapi import ExamScore
from wimsapi.api import WimsAPI
from wimsapi.exam import Exam
from wimsapi.exceptions import AdmRawError, NotSavedError
from wimsapi.user import User
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



class ExamTestCase(unittest.TestCase):
    
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
        e = Exam("Title", "Description")
        self.assertEqual(e.exo_count, 0)
        self.assertRaises(NotSavedError, lambda: e.infos)
        self.clas.save(WIMS_URL, "myself", "toto")
        self.clas.additem(e)
        self.assertIn("exam_title", e.infos)
    
    
    def test_get_exception(self):
        with self.assertRaises(NotSavedError):
            Exam.get(self.clas, 1)
        
        self.clas.save(WIMS_URL, "myself", "toto")
        with self.assertRaises(AdmRawError) as cm:
            Exam.get(self.clas, 50)
        self.assertIn("WIMS' server responded with an ERROR:", str(cm.exception))
    
    
    def test_save_and_refresh(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        e = Exam("Title", "Description")
        
        with self.assertRaises(NotSavedError):
            e.refresh()
        
        e.save(self.clas)
        
        s2 = Exam.get(self.clas, e.qexam)
        self.assertEqual(s2.title, "Title")
        
        e.title = "modified"
        e.save()
        
        self.assertEqual(e.title, "modified")
        self.assertEqual(s2.title, "Title")
        s2.refresh()
        self.assertEqual(s2.title, "modified")
    
    
    def test_check(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        e = Exam("Title", "Description")
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        
        with self.assertRaises(NotSavedError):
            Exam.check(c, e)
        
        self.assertFalse(Exam.check(self.clas, e))
        self.clas.additem(e)
        self.assertTrue(Exam.check(self.clas, e))
    
    
    def test_save_exceptions(self):
        e = Exam("Title", "Description")
        with self.assertRaises(NotSavedError):
            e.save()
        
        with self.assertRaises(NotSavedError):
            e.save(self.clas)
    
    
    def test_delete(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        e = Exam("Title", "Description")
        
        with self.assertRaises(NotSavedError):
            e.delete()
        
        e.save(self.clas)
        Exam.get(self.clas, e.qexam)  # Ok
        e.delete()
        with self.assertRaises(AdmRawError):
            Exam.get(self.clas, e.qexam)  # Should raise the exception
    
    
    def test_remove(self):
        self.clas.save(WIMS_URL, "myself", "toto")
        c = Class("myclass", "A class", "an institution", "mail@mail.com", "password",
                  self.user, qclass=999999)
        e = Exam("Title", "Description")
        
        with self.assertRaises(NotSavedError):
            e.remove(c, e)
        
        e.save(self.clas)
        Exam.get(self.clas, e.qexam)  # Ok
        Exam.remove(self.clas, e)
        with self.assertRaises(AdmRawError):
            Exam.get(self.clas, e.qexam)  # Should raise the exception
    
    
    def test_list(self):
        s1 = Exam("First", "First one")
        s2 = Exam("Second", "Second one")
        s3 = Exam("Third", "Third one")
        
        self.clas.save(WIMS_URL, "myself", "toto")
        
        self.assertListEqual(
            [],
            Exam.list(self.clas)
        )
        
        self.clas.additem(s1)
        self.clas.additem(s2)
        self.clas.additem(s3)
        
        self.assertListEqual(
            sorted([s1, s2, s3], key=lambda i: i.qexam),
            sorted(Exam.list(self.clas), key=lambda i: i.qexam)
        )
    
    
    def test_eq(self):
        s1 = Exam("First", "First one")
        s2 = Exam("Second", "Second one")
        s3 = Exam("Third", "Third one")
        
        self.clas.save(WIMS_URL, "myself", "toto")
        self.clas.additem(s1)
        self.clas.additem(s2)
        
        self.assertEqual(s1, self.clas.getitem(s1.qexam, Exam))
        self.assertNotEqual(s2, self.clas.getitem(s1.qexam, Exam))
        self.assertNotEqual(s2, 1)
        
        self.assertRaises(NotSavedError, lambda: s1 == s3)
    
    
    def test_scores(self):
        # Put a dummy class with existing scores if not already added
        qclass = 6948902
        if not Class.check(self.api.url, self.api.ident, self.api.passwd, qclass, "myclass"):
            archive = os.path.join(os.path.dirname(__file__), "resources/6948902.tgz")
            command("docker cp %s wims-minimal:/home/wims/log/classes/" % archive)
            command(
                'docker exec wims-minimal bash -c '
                '"tar -xzf /home/wims/log/classes/6948902.tgz -C /home/wims/log/classes/"'
            )
            command(
                'docker exec wims-minimal bash -c "chmod 644 /home/wims/log/classes/6948902/.def"'
            )
            command(
                'docker exec wims-minimal bash -c "chown wims:wims /home/wims/log/classes/6948902 '
                '-R"'
            )
            command('docker exec wims-minimal bash -c "rm /home/wims/log/classes/6948902.tgz"')
            command(
                "docker exec wims-minimal bash -c "
                "\"echo ':6948902,20200626,Institution,test,en,0,H4,dmi,S S,+myself/myclass+,' "
                '>> /home/wims/log/classes/.index"'
            )
        
        with self.assertRaises(NotSavedError):
            Exam().scores()
        
        c = Class.get(self.api.url, self.api.ident, self.api.passwd, qclass, "myclass")
        e = c.getitem(1, Exam)
        u = c.getitem("qcoumes", User)
        
        score = ExamScore(e, u, 6.67, 1)
        
        self.assertEqual(e.scores("qcoumes"), score)
        self.assertEqual(e.scores(), [score])
        
        with self.assertRaises(ValueError):
            e.scores("unknown")
