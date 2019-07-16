import datetime
import sys

from .exceptions import AdmRawError, NotSavedError
from .item import ClassItemABC
from .score import ExamScore
from .user import User
from .utils import one_year_later



class Exam(ClassItemABC):
    """This class is used to represent a WIMS' Exam.
    
    Parameters:
        title - (str) name of the exam (defaults to "Examen #n")
        description - (str) description of the exam (defaults to "Vous êtes dans l'examen n")
        expiration - (str) expiration date (yyyymmdd) defaults to one year later
        duration - (int) duration of each attempt of the exam in minutes (defaults to 60)
        attempts - (int) number of possible attempts for this exam (defaults to 1)"""
    
    
    def __init__(self, title=None, description=None, expiration=None, duration=60, attempts=1,
                 exammode=0, **kwargs):
        if expiration is not None:
            datetime.datetime.strptime(expiration, "%Y%m%d")
        
        super().__init__()
        self._class = None
        self._saved = False
        self.wclass = False
        self.qexam = sys.maxsize
        self.title = title
        self.description = description
        self.expiration = expiration if expiration is not None else one_year_later()
        self.attempts = attempts
        self.duration = duration
        self.exammode = exammode
        self.exos = []
    
    
    @property
    def exo_count(self):
        """Returns the number of exercises in this exam."""
        return len(self.exos)
    
    
    @property
    def infos(self):
        """Return all the informations hosted on the WIMS server about this exam."""
        if not self._class:
            raise NotSavedError("infos is not defined until the exam has been saved once")
        
        status, exam_info = self._class._api.getexam(
            self._class.qclass, self._class.rclass, self.qexam, verbose=True)
        if not status:
            raise AdmRawError(exam_info['message'])
        
        for k in ['status', 'code', 'job']:
            del exam_info[k]
        
        return exam_info
    
    
    def __str__(self):
        return "<wimsapi.Exam object at %s - qexam : %s>" % (hex(id(self)), str(self.qexam))
    
    
    __repr__ = __str__
    
    
    def __eq__(self, other):
        """Exams have to come from the same server and have the same qexam to be equal."""
        if isinstance(other, self.__class__):
            if not self.wclass or not other.wclass:
                raise NotSavedError("Cannot test equality between unsaved exams")
            return str(self.qexam) == str(other.qexam) and self._class == other._class
        return False
    
    
    def __hash__(self):
        if not self.wclass:
            raise NotSavedError("Unsaved User cannot be hashed")
        return hash((self._class.qclass, self.qexam))
    
    
    def refresh(self):
        """Refresh this instance of a WIMS Exam from the server itself."""
        if not self.wclass:
            raise NotSavedError("Can't refresh unsaved exam")
        
        new = Exam.get(self._class, self.qexam)
        self.__class__ = new.__class__
        self.__dict__ = new.__dict__
        
        return self
    
    
    def _to_payload(self):
        return {k: v for k, v in self.__dict__.items() if k not in ['qexam', '_saved', '_class']}
    
    
    def save(self, wclass=None, check_exists=True):
        """Save the Exam in the given class.

        wclass is an instance of wimsapi.Class. The argument is optionnal
        if the exam has already been saved or fetched from a Class, it
        will default to the last Class used to saved or the Class from which
        the exam was fetched.

        If check_exists is True, the api will check if a exam with the same ID
        exists on the WIMS' server. If it exists, save will instead modify this
        exam instead of trying to create new one."""
        if not wclass and not self._class:
            raise NotSavedError("wclass must be provided if this exam has neither been imported "
                                "from a WIMS class nor saved once yet")
        
        wclass = wclass or self._class
        
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to save a exam")
        
        if wclass is not None and check_exists:
            self._saved = wclass.checkitem(self)
        
        if self._saved:
            status, response = wclass._api.modexam(
                wclass.qclass, wclass.rclass, self.qexam, self._to_payload(), verbose=True)
        else:
            status, response = wclass._api.addexam(
                wclass.qclass, wclass.rclass, self._to_payload(), verbose=True)
        
        if not status:
            raise AdmRawError(response['message'])
        
        self.qexam = response['exam_id'] if "exam_id" in response else response["queryexam"]
        self._class = wclass
        self.wclass = True
    
    
    def delete(self):
        """Delete the exam from its associated WIMS class on the server."""
        if not self.wclass:
            raise NotSavedError("Cannot delete an unsaved exam")
        
        status, response = self._class._api.delexam(self._class.qclass, self._class.rclass,
                                                    self.qexam, verbose=True)
        if not status:
            raise AdmRawError(response['message'])
        
        self.wclass = False
        self._class = None
    
    
    @classmethod
    def check(cls, wclass, exam):
        """Returns True if exam is in wclass, False otherwise.

        exam can be either an instance of Exam, or an int corresponding to the identifier (qexam)
        of the Exam in the WIMS class.

        E.G. either Exam.check(wclass, 1) or Exam.check(wclass, Exam(...))"""
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to check whether a exam "
                                "exists")
        
        exam = exam.qexam if isinstance(exam, cls) else exam
        status, response = wclass._api.checkexam(wclass.qclass, wclass.rclass, exam,
                                                 verbose=True)
        msg = ('element #%s of type exam does not exist in this class (%s)'
               % (str(exam), str(wclass.qclass)))
        if not status and msg not in response['message']:  # pragma: no cover
            raise AdmRawError(response['message'])
        
        return status
    
    
    @classmethod
    def remove(cls, wclass, exam):
        """Remove the exam from wclass.

        exam can be either an instance of Exam, or an int corresponding to the identifier (qexam)
        of the Exam in the WIMS class.

        E.G. either Exam.remove(wclass, 1) or Exam.remove(wclass, Exam(...))"""
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to remove a exam")
        
        qexam = exam.qexam if isinstance(exam, cls) else exam
        status, response = wclass._api.delexam(wclass.qclass, wclass.rclass, qexam, verbose=True)
        if not status:
            raise AdmRawError(response['message'])
    
    
    @classmethod
    def get(cls, wclass, qexam):
        """Returns an instance of Exam corresponding to qexam in wclass."""
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to get a exam")
        
        status, exam_info = wclass._api.getexam(wclass.qclass, wclass.rclass, qexam,
                                                verbose=True)
        if not status:
            raise AdmRawError(exam_info['message'])
        
        duplicate = dict(exam_info)
        for k, v in duplicate.items():
            if k.startswith("exam_"):
                exam_info[k[5:]] = v
        exam_info["exammode"] = exam_info["exam_status"]
        
        exam = Exam(**exam_info)
        exam.qexam = exam_info["query_exam"]
        exam._class = wclass
        exam.wclass = True
        return exam
    
    
    @classmethod
    def list(cls, wclass):
        """Returns a list of every Exam of wclass."""
        status, response = wclass._api.listexams(wclass.qclass, wclass.rclass, verbose=True)
        if not status:
            raise AdmRawError(response['message'])
        
        return [cls.get(wclass, qexam) for qexam in response["examlist"] if qexam != '']
    
    
    def scores(self, user=None):
        """Returns a list of ExamScore for every user. If user is given returns only its
        SheetScore.
        
        user can either be an instance of wimsapi.User or its quser."""
        if not self.wclass:
            raise NotSavedError("Sheet must be saved before being able to retrieve scores")
        
        quser = user.quser if isinstance(user, User) else user
        if quser is not None and not self._class.checkitem(quser, User):  # Checks that quser exists
            raise ValueError("User '%s' does not exists in class '%s'" % (user, self._class.qclass))
        
        status, response = self._class._api.getexamscores(self._class.qclass, self._class.rclass,
                                                          self.qexam, verbose=True)
        if not status:
            raise AdmRawError(response['message'])
        
        scores = []
        for data in response["data_scores"]:
            if quser is not None and data['id'] != quser:
                continue
            user = self._class.getitem(data['id'], User)
            scores.append(ExamScore(self, user, data["score"], data["attempts"]))
        
        return scores[0] if quser is not None else scores
