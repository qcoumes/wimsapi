import datetime

from wimsapi.api import WimsAPI
from wimsapi.exceptions import AdmRawError, InvalidItemTypeError, NotSavedError
from wimsapi.item import ClassItemABC
from wimsapi.user import User
from wimsapi.utils import one_year_later


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



class Class:
    """This class is used to represent a WIMS' class.
    
    If provided, qclass will be the identifier of the newly created WIMS class when this instance
    is saved. The identifier is randomly chosen if qclass is not provided.
    
    Parameters:
        rclass - (str) identifier of the class on the sending server.
        name - (str) name of the class.
        institution - (str) name of the institution.
        email - (str) contact email address.
        password - (str) password for user registration.
        qclass - (int) identifier of the class on the receiving server.
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
    
    
    def __init__(self, rclass, name, institution, email, password, supervisor, qclass=None,
                 lang="en", expiration=None, limit=30, level="H4", secure='all', bgcolor='',
                 refcolor='', css='', **kwargs):
        if lang not in LANG:
            raise ValueError("lang must be one of wimsapi.class.LANG")
        if level not in LEVEL:
            raise ValueError("level must be in wimsapi.class.LEVEL")
        if expiration is not None:
            datetime.datetime.strptime(expiration, "%Y%m%d")
        
        self._api = None
        self._saved = False
        self.qclass = qclass
        self.rclass = rclass
        self.name = name
        self.institution = institution
        self.email = email
        self.password = password
        self.supervisor = supervisor
        self.lang = lang
        self.expiration = expiration if expiration is not None else one_year_later()
        self.limit = int(limit)
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
    
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if not self._api or not other._api:
                raise NotSavedError("Cannot test equality between unsaved classes")
            return self.refresh().qclass == other.refresh().qclass
        return False
    
    
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
            if not status:  # pragma: no cover
                raise AdmRawError(response['message'])
        else:
            status, response = self._api.addclass(
                self.rclass, payload, self.supervisor._to_payload(), self.qclass, verbose=True
            )
            if not status:  # pragma: no cover
                raise AdmRawError(response['message'])
            self.qclass = response['class_id']
            self.supervisor.quser = "supervisor"
        
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
        
        return self
    
    
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
        class_info['qclass'] = qclass
        c = cls(**class_info)
        c._api = api
        c._saved = True
        return c
    
    
    @classmethod
    def list(cls, url, ident, passwd, rclass):
        api = WimsAPI(url, ident, passwd)
        status, response = api.listclasses(rclass, verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(response['message'])
        
        qclasses = [c['qclass'] for c in response["classes_list"]]
        
        return [cls.get(url, ident, passwd, qclass, rclass) for qclass in qclasses]
    
    
    def additem(self, item):
        """Add an item to the WIMS class.
        
        Item must be a subclass of wimsapi.item.ClassItemABC."""
        if not issubclass(type(item), ClassItemABC):
            raise InvalidItemTypeError(
                "Item of type %s cannot be deleted from the WIMS class." % str(type(item)))
        if not self._saved:
            raise NotSavedError("Class must be saved before being able to add an item")
        
        item.save(self, check_exists=False)
    
    
    def delitem(self, item, cls=None):
        """Remove an item from the WIMS class.
        
        Item must be either a subclass of wimsapi.item.ClassItemABC or a
        string. If item is a string, cls must be provided and be a
        subclass of ClassItemABC which correspond to the item.
        
        E.G. for an user : delitem(User(...)) or delitem("quser", User)."""
        test = ((not isinstance(item, str) and not issubclass(type(item), ClassItemABC))
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
        test = ((not isinstance(item, str) and not issubclass(type(item), ClassItemABC))
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
    
    
    def listitem(self, cls):
        """Return all the instances of cls in, this WIMS class.
        
        cls must be a subclass of ClassItemABC"""
        if not issubclass(cls, ClassItemABC):
            raise InvalidItemTypeError(
                "Cannot list element of type %s from a WIMS class" % str(cls))
        if not self._saved:
            raise NotSavedError("Class must be saved  before being able to list items")
        
        return cls.list(self)
