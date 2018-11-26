from wimsapi.exceptions import AdmRawException



class User:
    
    def __init__(self, quser, lastname, firstname, password, email="", comments="", regnum="",
                 photourl="", participate="", courses="", classes="", supervise="",
                 supervisable="no",
                 external_auth="", agreecgu="yes", regprop1="", regprop2="", regprop3="",
                 regprop4="", regprop5="", **kwargs):
        self._class = None
        self._saved = False
        self.quser = quser
        self.lastname = lastname
        self.firstname = firstname
        self.password = password
        self.email = email
        self.comments = comments
        self.regnum = regnum
        self.photourl = photourl
        self.participate = participate
        self.courses = courses
        self.classes = classes
        self.supervise = supervise
        self.supervisable = supervisable
        self.external_auth = external_auth
        self.agreecgu = agreecgu
        self.regprop1 = regprop1
        self.regprop2 = regprop2
        self.regprop3 = regprop3
        self.regprop4 = regprop4
        self.regprop5 = regprop5
    
    
    @property
    def fullname(self):
        return (self.firstname + " " + self.lastname).title()
    
    
    @property
    def infos(self):
        if not self._class:
            raise ValueError("infos is not defined until the user has been saved once")
        status, user_info = self._class._api.getuser(
            self._class.qclass, self._class.rclass, self.quser)
        if not status:  # pragma: no cover
            raise AdmRawException(user_info['message'])
        
        for k in ['status', 'code', 'job']:
            del user_info[k]
        return user_info
    
    
    def refresh(self):
        """Refresh this instance of a WIMS User from the server itself."""
        if not self._saved:
            raise ValueError("Can't refresh unsaved user")
        new = User.get(self._class, self.quser)
        self.__class__ = new.__class__
        self.__dict__ = new.__dict__
    
    
    def _to_payload(self):
        return {k: v for k, v in self.__dict__.items() if k not in ['quser', '_api', '_class']}
    
    
    def save(self, wclass=None):
        if not wclass and not self._class:
            raise ValueError("wclass must be provided if User has not been imported from a WIMS"
                             " class.")
        
        wclass = wclass or self._class
        if not wclass._saved:
            raise ValueError("Class must be saved before being able to get / add an user.")
        
        if self._saved:
            status, response = wclass._api.moduser(
                wclass.qclass, wclass.rclass, self.quser, self._to_payload())
        else:
            status, response = wclass._api.adduser(
                wclass.qclass, wclass.rclass, self.quser, self._to_payload())

        if not status:  # pragma: no cover
            raise AdmRawException(response['message'])

        self._class = wclass
        self._saved = True
    
    
    def delete(self):
        if not self._class:
            raise ValueError("Can't delete unsaved user")
        
        c = self._class
        status, response = c._api.deluser(c.qclass, c.rclass, self.quser)
        
        if not status:  # pragma: no cover
            raise AdmRawException(response['message'])
    
    
    @classmethod
    def get(cls, wclass, quser):
        """Retrieve a wimsapi.user.User instance of the user corresponding to
        'quser' in wclass.

        Raise AdmRawException if the user corresponding to 'quser'
        in the class is not found."""
        if not wclass._saved:
            raise ValueError("Class must be saved before being able to get / add an user")
        
        status, user_info = wclass._api.getuser(wclass.qclass, wclass.rclass, quser)
        if not status:  # pragma: no cover
            raise AdmRawException(user_info['message'])
        
        status, user_password = wclass._api.getuser(wclass.qclass, wclass.rclass, quser,
                                                    ["password"])
        if not status:  # pragma: no cover
            raise AdmRawException(user_password['message'])
        
        user_info['password'] = user_password['password']
        user = cls(quser, **user_info)
        user._class = wclass
        user._saved = True
        return user
