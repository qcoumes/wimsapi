import datetime

from wimsapi.api import WimsAPI
from wimsapi.exceptions import AdmRawError, InvalidItemTypeError, NotSavedError
from wimsapi.item import ClassItemABC
from wimsapi.user import User


LANG = [
    'aa', 'ab', 'af', 'ak', 'sq', 'am', 'ar', 'an', 'hy', 'as', 'av', 'ae',
    'ay', 'az', 'ba', 'bm', 'eu', 'be', 'bn', 'bh', 'bi', 'bo', 'bs', 'br',
    'bg', 'my', 'ca', 'cs', 'ch', 'ce', 'zh', 'cu', 'cv', 'kw', 'co', 'cr',
    'cy', 'cs', 'da', 'de', 'dv', 'nl', 'dz', 'el', 'en', 'eo', 'et', 'eu',
    'ee', 'fo', 'fa', 'fj', 'fi', 'fr', 'fr', 'fy', 'ff', 'Ga', 'de', 'gd',
    'ga', 'gl', 'gv', 'el', 'gn', 'gu', 'ht', 'ha', 'he', 'hz', 'hi', 'ho',
    'hr', 'hu', 'hy', 'ig', 'is', 'io', 'ii', 'iu', 'ie', 'ia', 'id', 'ik',
    'is', 'it', 'jv', 'ja', 'kl', 'kn', 'ks', 'ka', 'kr', 'kk', 'km', 'ki',
    'rw', 'ky', 'kv', 'kg', 'ko', 'kj', 'ku', 'lo', 'la', 'lv', 'li', 'ln',
    'lt', 'lb', 'lu', 'lg', 'mk', 'mh', 'ml', 'mi', 'mr', 'ms', 'Mi', 'mk',
    'mg', 'mt', 'mn', 'mi', 'ms', 'my', 'na', 'nv', 'nr', 'nd', 'ng', 'ne',
    'nl', 'nn', 'nb', 'no', 'oc', 'oj', 'or', 'om', 'os', 'pa', 'fa', 'pi',
    'pl', 'pt', 'ps', 'qu', 'rm', 'ro', 'ro', 'rn', 'ru', 'sg', 'sa', 'si',
    'sk', 'sk', 'sl', 'se', 'sm', 'sn', 'sd', 'so', 'st', 'es', 'sq', 'sc',
    'sr', 'ss', 'su', 'sw', 'sv', 'ty', 'ta', 'tt', 'te', 'tg', 'tl', 'th',
    'bo', 'ti', 'to', 'tn', 'ts', 'tk', 'tr', 'tw', 'ug', 'uk', 'ur', 'uz',
    've', 'vi', 'vo', 'cy', 'wa', 'wo', 'xh', 'yi', 'yo', 'za', 'zh', 'zu',
]

LEVEL = [
    "E1", "E2", "E3", "E4", "E5", "E6",
    "H1", "H2", "H3", "H4", "H5", "H6",
    "U1", "U2", "U3", "U4", "U5",
    "G", "R",
]



def one_year_later():
    """Give the date one year later from now in the format yyyymmdd."""
    d = datetime.date.today()
    return d.replace(year=d.year + 1).strftime("%Y%m%d")



class Class:
    """This class is used to represent a WIMS' class.
    
    Parameters:
        qclass - (int) identifier of the class on the receiving server.
        rclass - (str) identifier of the class on the sending server.
        name - (str) name of the class.
        institution - (str) name of the institution.
        email - (str) contact email address.
        password - (str) password for user registration.
        supervisor - (wimsapi.user.User) An WIMS user instance representing the supervisor.
        lang - (str) class language (en, fr, es, it, etc).
        expiration - (str) class expiration date (yyyymmdd, defaults to one year later).
        limit - (str) limit of number of participants (defaults to 30).
        level - (str) level of the class (defaults to H4) Valid levels: E1,
                          E2, ..., E6, H1, ..., H6, U1, ..., U5, G, R
        secure - (str) secure hosts.
        bgcolor - (str) page background color.
        refcolor - (str) menu background color.
        css - (str) css file (must be existing css on the WIMS server)."""
    
    
    def __init__(self, qclass, rclass, name, institution, email, password, supervisor, lang="en",
                 date=None, limit=30, level="H4", secure='all', bgcolor='', refcolor='',
                 css='', **kwargs):
        if lang not in LANG:
            raise ValueError("lang must be one of wimsapi.class.LANG")
        if level not in LEVEL:
            raise ValueError("level must be in wimsapi.class.LEVEL")
        try:
            if date is not None:
                datetime.datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise ValueError("Given date not in the format 'yyyymmdd'")
        
        self._api = None
        self._saved = False
        self.qclass = qclass
        self.rclass = rclass
        self.name = name
        self.institution = institution
        self.email = email
        self.password = password
        self.supervisor = supervisor
        self.date = date if date is not None else one_year_later()
        self.limit = limit
        self.level = level
        self.secure = secure
        self.bgcolor = bgcolor
        self.refcolor = refcolor
        self.css = css
    
    
    def __contains__(self, item):
        """check if an item is in the WIMS class.
        
        Item must be a subclass of wimsapi.item.ClassItemABC."""
        if issubclass(type(item), ClassItemABC):
            if not self._saved:
                raise NotSavedError("Cannot use 'in' operator with an unsaved class.")
            return self.checkitem(item)
        
        return NotImplemented  # pragma: no cover
    
    
    def _to_payload(self):
        """Return a dictionnary representing this class as defined in adm/raw."""
        d = {k: v for k, v in self.__dict__.items()
             if k not in ['qclass', 'rclass', 'supervisor', '_api', 'wclass']}
        d['description'] = d['name']
        d['supervisor'] = self.supervisor.fullname
        del d['name']
        return d
    
    
    @property
    def url(self):
        """Return the url of the server hosting this WIMS class. Raise ValueError
        if the class has not been saved yet."""
        if not self._api:
            raise NotSavedError("url is not defined until the WIMS class is saved once")
        return self._api.url
    
    
    @property
    def ident(self):
        """Return the ident used on the server hosting this WIMS class. Raise ValueError
        if the class has not been saved yet."""
        if not self._api:
            raise NotSavedError("ident is not defined until the WIMS class is saved once")
        return self._api.ident
    
    
    @property
    def passwd(self):
        """Return the passwd used on the server hosting this WIMS class. Raise ValueError
        if the class has not been saved yet."""
        if not self._api:
            raise NotSavedError("passwd is not defined until the WIMS class is saved once")
        return self._api.passwd
    
    
    @property
    def infos(self):
        """Return all the informations hosted on the WIMS server about this class."""
        if not self._api:
            raise NotSavedError("infos is not defined until the WIMS class is saved once")
        status, class_info = self._api.getclass(self.qclass, self.rclass, verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(class_info['message'])
        
        for k in ['status', 'code', 'job']:
            del class_info[k]
        return class_info
    
    
    def save(self, url=None, ident=None, passwd=None):
        """Save this the modification done on this class on the WIMS server.
        
        If the class has not been obtain through the get() method and has never been
        saved yet, arguments url, ident and passwd must be provided.
        
        Use the method refresh() on any other instance representing this class
        to reflect the change saved."""
        if url and ident and passwd:
            self._api = WimsAPI(url, ident, passwd)
        
        if not self._api:
            raise NotSavedError("url, ident and passwd must be provided when saving for the first "
                                "time.")
        
        payload = self._to_payload()
        
        if self._saved:
            status, response = self._api.modclass(self.qclass, self.rclass, payload, verbose=True)
        else:
            status, response = self._api.addclass(self.qclass, self.rclass, payload,
                                                  self.supervisor._to_payload(), verbose=True)
            self.supervisor.quser = "supervisor"
        
        if not status:  # pragma: no cover
            raise AdmRawError(response['message'])
        
        self._saved = True
    
    
    def delete(self):
        """Delete the class from the WIMS server."""
        if not self._saved:
            raise NotSavedError("Can't delete unsaved class")
        
        status, response = self._api.delclass(self.qclass, self.rclass, verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(response['message'])
        
        self._saved = False
        self._api = None
    
    
    def refresh(self):
        """Refresh this instance of a WIMS class from the server itself."""
        if not self._saved:
            raise NotSavedError("Can't refresh unsaved class")
        new = Class.get(self.url, self.ident, self.passwd, self.qclass, self.rclass)
        self.__class__ = new.__class__
        self.__dict__ = new.__dict__
    
    
    @classmethod
    def get(cls, url, ident, passwd, qclass, rclass):
        """Return an instance of a WIMS class corresponding to the class 'qclass' on
        the WIMS server pointed by 'url'."""
        api = WimsAPI(url, ident, passwd)
        
        status, class_info = api.getclass(qclass, rclass, verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(class_info['message'])
        
        status, class_password = api.getclass(qclass, rclass, verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(class_password['message'])
        
        status, supervisor_info = api.getuser(qclass, rclass, "supervisor", verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(supervisor_info['message'])
        
        status, password_info = api.getuser(qclass, rclass, "supervisor", ["password"],
                                            verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(password_info['message'])
        
        supervisor_info['password'] = password_info['password']
        supervisor = User("supervisor", **supervisor_info)
        
        class_info['supervisor'] = supervisor
        class_info['name'] = class_info['description']
        class_info['password'] = class_password['password']
        
        c = cls(qclass, **class_info)
        c._api = api
        c._saved = True
        return c
    
    
    def additem(self, item):
        """Add an item to the WIMS class.
        
        Item must be a subclass of wimsapi.item.ClassItemABC."""
        if not issubclass(type(item), ClassItemABC):
            raise InvalidItemTypeError(
                "Item of type %s cannot be deleted from the WIMS class." % str(type(item)))
        if not self._saved:
            raise NotSavedError("Class must be saved before being able to add an item")
        
        item.save(self)
    
    
    def delitem(self, item, cls=None):
        """Remove an item from the WIMS class.
        
        Item must be either a subclass of wimsapi.item.ClassItemABC or a
        string. If item is a string, cls must be provided and be a
        subclass of ClassItemABC which correspond to the item.
        
        E.G. for an user : delitem(User(...)) or delitem("quser", User)."""
        test = ((type(item) is not str and not issubclass(type(item), ClassItemABC))
                or (cls is not None and not issubclass(cls, ClassItemABC)))
        if test:
            raise InvalidItemTypeError(
                "Item of type %s cannot be deleted from the WIMS class"
                % str(type(item) if type(item) is not str else cls))
        if not self._saved:
            raise NotSavedError("Class must be saved before being able to remove an item")
        
        cls = cls or type(item)
        cls.remove(self, item)
    
    
    def checkitem(self, item, cls=None):
        """check if an item is in the WIMS class.
        
        Item must be either a subclass of wimsapi.item.ClassItemABC or a
        string. If item is a string, cls must be provided and be a
        subclass of ClassItemABC which correspond to the item.
        
        E.G. for an user : checkitem(User(...)) or checkitem("quser", User)."""
        test = ((type(item) is not str and not issubclass(type(item), ClassItemABC))
                or (cls is not None and not issubclass(cls, ClassItemABC)))
        if test:
            raise InvalidItemTypeError(
                "Cannot check if an item of type %s is in a WIMS class"
                % str(type(item) if type(item) is not str else cls))
        if not self._saved:
            raise NotSavedError("Class must be saved before being able to check whether an item "
                                "exists")
        
        cls = cls or type(item)
        return cls.check(self, item)
    
    
    def getitem(self, identifier, cls):
        """Return the instance of cls corresponding to identifier in the WIMS
        class.
        
        cls must be a subclass of ClassItemABC which correspond to the item
        identified by identier."""
        if not issubclass(cls, ClassItemABC):
            raise InvalidItemTypeError("Cannot get element of type %s from a WIMS class" % str(cls))
        if not self._saved:
            raise NotSavedError("Class must be saved before being able to get an item")
        
        return cls.get(self, identifier)
