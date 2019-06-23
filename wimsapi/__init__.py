# -*- coding: utf-8 -*-

from .api import WimsAPI
from .exceptions import AdmRawError, InvalidItemTypeError, NotSavedError, WimsAPIError
from .sheet import Sheet
from .user import User
from .wclass import Class
from .exam import Exam


name = "wimsapi"
__title__ = 'wimsapi'
__version__ = VERSION = '0.4.1'
