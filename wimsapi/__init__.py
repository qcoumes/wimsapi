from .api import WimsAPI
from .exam import Exam
from .exceptions import AdmRawError, InvalidItemTypeError, NotSavedError, WimsAPIError
from .score import ExamScore, ExerciseScore, SheetScore
from .sheet import Sheet
from .user import User
from .wclass import Class


name = "wimsapi"
__title__ = 'wimsapi'
__version__ = VERSION = '0.5.2'
