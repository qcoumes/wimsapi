import datetime

from wimsapi.api import WimsAPI
from wimsapi.user import User
from wimsapi.exceptions import AdmRawException


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
        self.date = date if date is not None else datetime.date.today().strftime("%Y%m%d")
        self.limit = limit
        self.level = level
        self.secure = secure
        self.bgcolor = bgcolor
        self.refcolor = refcolor
        self.css = css
    
    
    def _to_payload(self):
        d = {k: v for k, v in self.__dict__.items()
             if k not in ['qclass', 'rclass', 'supervisor', '_api', '_saved']}
        d['description'] = d['name']
        d['supervisor'] = self.supervisor.fullname
        del d['name']
        return d
    
    
    @property
    def url(self):
        if not self._api:
            raise ValueError("url is not defined until the wims class is saved once")
        return self._api.url
    
    
    @property
    def ident(self):
        if not self._api:
            raise ValueError("ident is not defined until the wims class is saved once")
        return self._api.ident
    
    
    @property
    def passwd(self):
        if not self._api:
            raise ValueError("passwd is not defined until the wims class is saved once")
        return self._api.passwd
    
    
    @property
    def infos(self):
        status, class_info = self._api.getclass(self.qclass, self.rclass)
        if not status:
            raise AdmRawException(class_info['message'])
        
        for k in ['status', 'code', 'job']:
            del class_info[k]
        return class_info
    
    
    def save(self, url=None, ident=None, passwd=None):
        if url and ident and passwd:
            self._api = WimsAPI(url, ident, passwd)
        
        if not self._api:
            raise ValueError("url, ident and passwd must be provided when saving for the first "
                             "time.")
        
        payload = self._to_payload()
        
        if self._saved:
            status, response = self._api.modclass(self.qclass, self.rclass, payload)
        else:
            status, response = self._api.addclass(self.qclass, self.rclass, payload,
                                                  self.supervisor._to_payload())
            self._saved = True
        if not status:
            raise AdmRawException(response['message'])
    
    
    def refresh(self):
        self = self.get(self.url, self.ident, self.passwd, self.qclass, self.rclass)
    
    
    @classmethod
    def get(cls, url, ident, passwd, qclass, rclass):
        api = WimsAPI(url, ident, passwd)
        
        status, class_info = api.getclass(qclass, rclass)
        if not status:
            raise AdmRawException(class_info['message'])
        
        status, class_password = api.getclass(qclass, rclass)
        if not status:
            raise AdmRawException(class_password['message'])
        
        status, supervisor_info = api.getuser(qclass, rclass, "supervisor")
        if not status:
            raise AdmRawException(supervisor_info['message'])
        
        status, password_info = api.getuser(qclass, rclass, "supervisor", ["password"])
        if not status:
            raise AdmRawException(password_info['message'])
        
        supervisor_info['password'] = password_info['password']
        supervisor = User("supervisor", **supervisor_info)
        
        class_info['supervisor'] = supervisor
        class_info['name'] = class_info['description']
        class_info['password'] = class_password['password']
        
        c = cls(qclass, **class_info)
        c._api = api
        c._saved = True
        return c
    
    
    def get_user(self, quser):
        if not self._saved:
            raise ValueError("Class must be saved before being able to get / add an user.")
        status, user_info = self._api.getuser(self.qclass, self.rclass, quser)
        if not status:
            raise AdmRawException(user_info['message'])
        status, user_password = self._api.getuser(self.qclass, self.rclass, quser, ["password"])
        if not status:
            raise AdmRawException(user_password['message'])

        user_info['password'] = user_password['password']
        user = User("supervisor", **user_info)
        user._class = self
        return user
