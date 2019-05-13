import datetime
import sys

from wimsapi.exceptions import AdmRawError, NotSavedError
from wimsapi.item import ClassItemABC
from wimsapi.utils import one_year_later



class Sheet(ClassItemABC):
    """This class is used to represent a WIMS' Worksheet.

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
                  The semicolons (;) in this parameter will be
                  interpreted as new lines. Equal characters (=) must
                  be replaced by the character AT (@).
                  There is no check made, so the integrity of the
                  contents is up to you only! (defaults to "")"""
    
    
    def __init__(self, title, description, expiration=None, sheetmode=0, weight=1,
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
        if not status:  # pragma: no cover
            raise AdmRawError(sheet_info['message'])
        
        for k in ['status', 'code', 'job']:
            del sheet_info[k]
        
        return sheet_info
    
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if not self.wclass or not other.wclass:
                raise NotSavedError("Cannot test equality between unsaved sheets")
            return self.refresh().qsheet == other.refresh().qsheet
        
        return False
    
    
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
        
        if not status:  # pragma: no cover
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
        if not status:  # pragma: no cover
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
        
        sheet = sheet.qsheet if type(sheet) is cls else sheet
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
        
        qsheet = sheet.qsheet if type(sheet) is cls else sheet
        status, response = wclass._api.delsheet(wclass.qclass, wclass.rclass, qsheet, verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(response['message'])
    
    
    @classmethod
    def get(cls, wclass, qsheet):
        """Returns an instance of Sheet corresponding to qsheet in wclass."""
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to get a sheet")
        
        status, sheet_info = wclass._api.getsheet(wclass.qclass, wclass.rclass, qsheet,
                                                  verbose=True)
        if not status:  # pragma: no cover
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
        status, response = wclass._api.listsheets(wclass.qclass, wclass.rclass, verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(response['message'])
        
        return [cls.get(wclass, qsheet) for qsheet in response["sheetlist"] if qsheet != '']
