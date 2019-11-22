import os
import unittest

from wimsapi import Exam, ExamScore, ExerciseScore, Sheet, SheetScore, User


WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi/"



class SheetTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.user = User("supervisor", "last", "first", "pass", "mail@mail.com")
        cls.sheet = Sheet()
        cls.sheet.qsheet = 1
        cls.exam = Exam()
        cls.exam.qexam = 1
    
    
    def test_exercise_score_eq(self):
        self.assertEqual(
            ExerciseScore(None, self.user, 10, 10, 10, 10, 10, 10, 1, 1),
            ExerciseScore(None, self.user, 10, 10, 10, 10, 10, 10, 1, 1)
        )
        self.assertNotEqual(
            ExerciseScore(None, self.user, 10, 10, 10, 10, 10, 10, 1, 1),
            ExerciseScore(None, self.user, 10, 9, 10, 10, 10, 10, 1, 1)
        )
        self.assertNotEqual(
            ExerciseScore(None, self.user, 10, 10, 10, 10, 10, 10, 1, 1),
            None
        )
    
    
    def test_sheet_score_eq(self):
        self.assertEqual(
            SheetScore(self.sheet, self.user, 10, 10, 10, 10, 10, 1, []),
            SheetScore(self.sheet, self.user, 10, 10, 10, 10, 10, 1, [])
        )
        self.assertNotEqual(
            SheetScore(self.sheet, self.user, 10, 10, 10, 10, 10, 1, []),
            SheetScore(self.sheet, self.user, 8, 10, 10, 10, 10, 1, [])
        )
        self.assertNotEqual(
            SheetScore(self.sheet, self.user, 10, 10, 10, 10, 10, 1, []),
            None
        )
    
    
    def test_exam_score_eq(self):
        self.assertEqual(
            ExamScore(self.exam, self.user, 10, 1),
            ExamScore(self.exam, self.user, 10, 1)
        )
        self.assertNotEqual(
            ExamScore(self.exam, self.user, 10, 1),
            ExamScore(self.exam, self.user, 10, 2)
        )
        self.assertNotEqual(
            ExamScore(self.exam, self.user, 10, 1),
            None
        )
