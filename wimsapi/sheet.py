import datetime
import sys

from .exceptions import AdmRawError, NotSavedError
from .item import ClassItemABC
from .score import ExerciseScore, SheetScore
from .user import User
from .utils import default, one_year_later



class Sheet(ClassItemABC):
    """This class is used to represent a WIMS' Worksheet.
    
    Parameters:
        title - (str) name of the sheet (defaults to "sheet n#")
        description - (str) description of the sheet (defaults to "sheet n#")
        expiration - (str) expiration date (yyyymmdd) defaults to one year later
        sheetmode - (str) the mode of the sheet:
            0 : pending (default)
            1 : active
            2 : expired
            3 : expired + hidden
        weight - (int) weight of the sheet in the class score (default to 1), use 0 if you want this
            sheet's score to be ignored.
        formula - (str) How the score is calculated for this sheet (0 to 6, default to 2)
            0 : Very lenient: maximum between percentage and quality.
            1 : Quality is not taken into account. You get maximum of grade once all
                the required work is done.
            2 : Quality has only slight effect over the grade.
            3 : More effect of quality.
            4 : To have a grade of 10, you must gather all required points (100%)
                without making any error (quality=10).
            5 : Unfinished work is over-punished.
            6 : Any mistake is over-punished.
        indicator - (str) what indicator will be used in the score formula (0 to 2, default to 1)
        contents - (str) the contents for the multi-line file to be created.
            The semicolons (;) in this parameter will be interpreted as new lines. Equal characters
            (=) must be replaced by the character AT (@). There is no check made, so the integrity
            of the contents is up to you only! (defaults to "")"""
    
    
    def __init__(self, title=None, description=None, expiration=None, sheetmode=0, weight=1,
                 formula=2, indicator=1, contents="", **kwargs):
        if expiration is not None:
            datetime.datetime.strptime(expiration, "%Y%m%d")
        
        super().__init__()
        self._class = None
        self._saved = False
        self.wclass = False
        self.qsheet = sys.maxsize
        self.title = title
        self.description = description
        self.expiration = expiration if expiration is not None else one_year_later()
        self.sheetmode = sheetmode
        self.weight = weight
        self.formula = formula
        self.indicator = indicator
        self.contents = contents
        self.exos = []
    
    
    @property
    def exo_count(self):
        """Returns the number of exercises in this sheet."""
        return len(self.exos)
    
    
    @property
    def infos(self):
        """Return all the informations hosted on the WIMS server about this sheet."""
        if not self._class:
            raise NotSavedError("infos is not defined until the sheet has been saved once")
        
        status, sheet_info = self._class._api.getsheet(
            self._class.qclass, self._class.rclass, self.qsheet, verbose=True)
        if not status:
            raise AdmRawError(sheet_info['message'])
        
        for k in ['status', 'code', 'job']:
            del sheet_info[k]
        
        return sheet_info
    
    
    def __str__(self):
        return "<wimsapi.Sheet object at %s - qsheet : %s>" % (hex(id(self)), str(self.qsheet))
    
    
    __repr__ = __str__
    
    
    def __eq__(self, other):
        """Sheets have to come from the same server and have the same qsheet to be equal."""
        if isinstance(other, self.__class__):
            if not self.wclass or not other.wclass:
                raise NotSavedError("Cannot test equality between unsaved sheets")
            return str(self.qsheet) == str(other.qsheet) and self._class == other._class
        return False
    
    
    def __hash__(self):
        if not self.wclass:
            raise NotSavedError("Unsaved User cannot be hashed")
        return hash((self._class.qclass, self.qsheet))
    
    
    def refresh(self):
        """Refresh this instance of a WIMS Sheet from the server itself."""
        if not self.wclass:
            raise NotSavedError("Can't refresh unsaved sheet")
        
        new = Sheet.get(self._class, self.qsheet)
        self.__class__ = new.__class__
        self.__dict__ = new.__dict__
        
        return self
    
    
    def _to_payload(self):
        return {k: v for k, v in self.__dict__.items() if k not in ['qsheet', '_saved', '_class']}
    
    
    def save(self, wclass=None, check_exists=True):
        """Save the Sheet in the given class.

        wclass is an instance of wimsapi.Class. The argument is optionnal
        if the sheet has already been saved or fetched from a Class, it
        will default to the last Class used to saved or the Class from which
        the sheet was fetched.
        
        If check_exists is True, the api will check if a sheet with the same ID
        exists on the WIMS' server. If it exists, save will instead modify this
        sheet instead of trying to create new one."""
        if not wclass and not self._class:
            raise NotSavedError("wclass must be provided if this sheet has neither been imported "
                                "from a WIMS class nor saved once yet")
        
        wclass = wclass or self._class
        
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to save a sheet")
        
        if wclass is not None and check_exists:
            self._saved = wclass.checkitem(self)
        
        if self._saved:
            status, response = wclass._api.modsheet(
                wclass.qclass, wclass.rclass, self.qsheet, self._to_payload(), verbose=True)
        else:
            status, response = wclass._api.addsheet(
                wclass.qclass, wclass.rclass, self._to_payload(), verbose=True)
        
        if not status:
            raise AdmRawError(response['message'])
        
        self.qsheet = response['sheet_id'] if "sheet_id" in response else response["querysheet"]
        self._class = wclass
        self.wclass = True
    
    
    def delete(self):
        """Delete the sheet from its associated WIMS class on the server."""
        if not self.wclass:
            raise NotSavedError("Cannot delete an unsaved sheet")
        
        status, response = self._class._api.delsheet(self._class.qclass, self._class.rclass,
                                                     self.qsheet, verbose=True)
        if not status:
            raise AdmRawError(response['message'])
        
        self.wclass = False
        self._class = None
    
    
    @classmethod
    def check(cls, wclass, sheet):
        """Returns True if sheet is in wclass, False otherwise.

        sheet can be either an instance of Sheet, or an int corresponding to the identifier (qsheet)
        of the Sheet in the WIMS class.

        E.G. either Sheet.check(wclass, 1) or Sheet.check(wclass, Sheet(...))"""
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to check whether a sheet "
                                "exists")
        
        sheet = sheet.qsheet if isinstance(sheet, cls) else sheet
        status, response = wclass._api.checksheet(wclass.qclass, wclass.rclass, sheet,
                                                  verbose=True)
        msg = ('element #%s of type sheet does not exist in this class (%s)'
               % (str(sheet), str(wclass.qclass)))
        if not status and msg not in response['message']:  # pragma: no cover
            raise AdmRawError(response['message'])
        
        return status
    
    
    @classmethod
    def remove(cls, wclass, sheet):
        """Remove the sheet from wclass.

        sheet can be either an instance of Sheet, or an int corresponding to the identifier (qsheet)
        of the Sheet in the WIMS class.

        E.G. either Sheet.remove(wclass, 1) or Sheet.remove(wclass, Sheet(...))"""
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to remove a sheet")
        
        qsheet = sheet.qsheet if isinstance(sheet, cls) else sheet
        status, response = wclass._api.delsheet(wclass.qclass, wclass.rclass, qsheet, verbose=True)
        if not status:
            raise AdmRawError(response['message'])
    
    
    @classmethod
    def get(cls, wclass, qsheet):
        """Returns an instance of Sheet corresponding to qsheet in wclass."""
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to get a sheet")
        
        status, sheet_info = wclass._api.getsheet(wclass.qclass, wclass.rclass, qsheet,
                                                  verbose=True)
        if not status:
            raise AdmRawError(sheet_info['message'])
        
        duplicate = dict(sheet_info)
        for k, v in duplicate.items():
            if k.startswith("sheet_"):
                sheet_info[k[6:]] = v
        sheet_info["sheetmode"] = sheet_info["sheet_status"]
        
        sheet = Sheet(**sheet_info)
        sheet.qsheet = sheet_info["query_sheet"]
        sheet._class = wclass
        sheet.wclass = True
        return sheet
    
    
    @classmethod
    def list(cls, wclass):
        """Returns a list of every Sheet of wclass."""
        status, response = wclass._api.listsheets(wclass.qclass, wclass.rclass, verbose=True)
        if not status:
            raise AdmRawError(response['message'])
        
        return [cls.get(wclass, qsheet) for qsheet in response["sheetlist"] if qsheet != '']
    
    
    @staticmethod
    def _compute_grade(formula, i, Q, cumul, best, acquired):
        """Compute the grade of a sheet according to the formula and the chosen I.
        
        Formula contains both Q and I."""
        i = int(i)
        if i == 0:
            I = cumul
        elif i == 1:
            I = best
        else:
            I = acquired
        
        Q /= 10
        I /= 100
        formula = "10 * (%s)" % formula
        return round(eval(formula.replace("^", "**")), 2)
    
    
    def scores(self, user=None):
        """Returns a list of SheetScore for every user. If user is given returns only its
        SheetScore.
        
        user can either be an instance of wimsapi.User or its quser.
        
        A value of -1 on some members mean that WIMS did not send the value. This may be caused
        by an outdated WIMS server."""
        if not self.wclass:
            raise NotSavedError("Sheet must be saved before being able to retrieve scores")
        
        quser = user.quser if isinstance(user, User) else user
        if quser is not None and not self._class.checkitem(quser, User):  # Checks that quser exists
            raise ValueError("User '%s' does not exists in class '%s'" % (user, self._class.qclass))
        
        status, response = self._class._api.getsheetscores(self._class.qclass, self._class.rclass,
                                                           self.qsheet, verbose=True)
        if not status:
            raise AdmRawError(response['message'])
        
        scores = []
        exo_count = len(response["exo_weights" if "exo_weights" in response else "weights"])
        for data in response["data_scores"]:
            if quser is not None and data['id'] != quser:
                continue
            
            user = self._class.getitem(data['id'], User)
            try:
                score = self._compute_grade(response["sheet_formula"]["formula"],
                                            response["sheet_formula"]["I"], data["user_quality"],
                                            data["user_percent"], data["user_best"],
                                            data["user_level"])
            except Exception:  # pragma: no cover
                score = -1
            
            sheet_params = {
                "sheet":     self,
                "user":      user,
                "score":     score,
                "quality":   data.get("user_quality", -1),
                "cumul":     data.get("user_percent", -1),
                "best":      data.get("user_best", -1),
                "acquired":  data.get("user_level", -1),
                "weight":    self.weight,
                "exercises": [],
            }
            for i in range(exo_count):
                exo_params = {
                    "exo":      None,
                    "user":     user,
                    "quality":  default(data, "mean_detail", i, -1),
                    "cumul":    default(data, "got_detail", i, -1),
                    "best":     default(data, "best_detail", i, -1),
                    "acquired": default(data, "level_detail", i, -1),
                    "last":     default(data, "last_detail", i, -1),
                    "tries":    default(data, "try_detail", i, -1),
                    "weight":   default(response, "exo_weights", i, -1),
                    "required": default(response, "requires", i, -1),
                }
                sheet_params["exercises"].append(ExerciseScore(**exo_params))
            
            scores.append(SheetScore(**sheet_params))
        
        return scores[0] if quser is not None else scores
