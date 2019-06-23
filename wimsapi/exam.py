import datetime
import sys

from wimsapi.exceptions import AdmRawError, NotSavedError
from wimsapi.item import ClassItemABC
from wimsapi.utils import one_year_later



class Exam(ClassItemABC):