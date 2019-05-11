from wimsapi.exceptions import AdmRawError, NotSavedError
from wimsapi.item import ClassItemABC



class User(ClassItemABC):
    """This class is used to represent a WIMS' user.

    Parameters:
        quser  - (str) user identifier on the receiving server.
        lastname - (str) last name of the user.
        firstname - (str) first name of the user.
        password - (str) user's password, non-crypted.
        email - (str) email address.
        comments - (str) any comments.
        regnum - (str) registration number.
        photourl - (str) url of user's photo.
        participate - (str) list classes where user participates.
        courses - (str) special for portal.
        classes - (str) special for portal.
        supervise - (str) List classes where teacher are administator.
        supervisable - (str) yes/no ; give right to the user to supervise a class (default to 'no').
        external_auth - (str) login for external_auth.
        agreecgu - (str) yes/ no ; if yes, the user will not be asked when he enters
                         for the first time to agree the cgu (default to "yes").
        regprop[1..5] - (str) custom variables."""
    
    
    def __init__(self, quser, lastname, firstname, password, email="", comments="", regnum="",
                 photourl="", participate="", courses="", classes="", supervise="",
                 supervisable="no", external_auth="", agreecgu="yes", regprop1="", regprop2="",
                 regprop3="", regprop4="", regprop5="", **kwargs):
        super().__init__()
        self._class = None
        self._saved = False
        self.wclass = False
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
        """Return all the informations hosted on the WIMS server about this user."""
        if not self._class:
            raise NotSavedError("infos is not defined until the user has been saved once")
        
        status, user_info = self._class._api.getuser(
            self._class.qclass, self._class.rclass, self.quser, verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(user_info['message'])
        
        for k in ['status', 'code', 'job']:
            del user_info[k]
        
        return user_info
    
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if not self.wclass or not other.wclass:
                raise NotSavedError("Cannot test equality between unsaved users")
            return self.refresh().quser == other.refresh().quser
        return False
    
    
    def refresh(self):
        """Refresh this instance of a WIMS User from the server itself."""
        if not self.wclass:
            raise NotSavedError("Can't refresh unsaved user")
        
        new = User.get(self._class, self.quser)
        self.__class__ = new.__class__
        self.__dict__ = new.__dict__
        
        return self
    
    
    def _to_payload(self):
        return {k: v for k, v in self.__dict__.items() if k not in ['quser', '_class', '_saved']}
    
    
    def save(self, wclass=None, check_exists=True):
        """Save the User in the given class.
        
        wclass is an instance of wimsapi.Class. The argument is optionnal
        if the user has already been saved or fetched from a Class, it
        will default to the last Class used to saved or the Class from which
        the user was fetched.
        
        If check_exists is True, the api will check if an user with the same ID
        exists on the WIMS' server. If it exists, save will instead modify this
        user instead of trying to create new one."""
        if not wclass and not self._class:
            raise NotSavedError("wclass must be provided if this user has neither been imported "
                                "from a WIMS class nor saved once yet")
        
        wclass = wclass or self._class
        
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to save an user")
        
        if wclass is not None and check_exists:
            self._saved = wclass.checkitem(self)
        
        if self._saved:
            status, response = wclass._api.moduser(
                wclass.qclass, wclass.rclass, self.quser, self._to_payload(), verbose=True)
        else:
            status, response = wclass._api.adduser(
                wclass.qclass, wclass.rclass, self.quser, self._to_payload(), verbose=True)
        
        if not status:  # pragma: no cover
            raise AdmRawError(response['message'])
        
        self._class = wclass
        self.wclass = True
    
    
    def delete(self):
        """Delete the user from its associated WIMS class on the server."""
        if not self.wclass:
            raise NotSavedError("Cannot delete an unsaved user")
        
        status, response = self._class._api.deluser(self._class.qclass, self._class.rclass,
                                                    self.quser, verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(response['message'])
        
        self.wclass = False
        self._class = None
    
    
    @classmethod
    def check(cls, wclass, user):
        """Returns True if item is in wclass, False otherwise.

        user can be either an instance of User, or string corresponding to the identifier (quser)
        of the User in the WIMS class.

        E.G. either User.check(wclass, "quser") or User.check(wclass, User(...))"""
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to check whether an user "
                                "exists")
        
        quser = user.quser if isinstance(user, cls) else user
        status, response = wclass._api.checkuser(wclass.qclass, wclass.rclass, quser, verbose=True)
        msg = 'user %s not in this class (%s)' % (str(quser), str(wclass.qclass))
        if not status and msg not in response['message']:  # pragma: no cover
            raise AdmRawError(response['message'])
        
        return status
    
    
    @classmethod
    def remove(cls, wclass, user):
        """Remove the user from wclass.

        user can be either an instance of User, or a string corresponding to the identifier (quser)
        of the User in the WIMS class.

        E.G. either User.remove(wclass, "quser") or User.remove(wclass, User(...))"""
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to remove an user")
        
        quser = user.quser if isinstance(user, cls) else user
        status, response = wclass._api.deluser(wclass.qclass, wclass.rclass, quser, verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(response['message'])
    
    
    @classmethod
    def get(cls, wclass, quser):
        """Returns an instance of User corresponding to quser in wclass."""
        if not wclass._saved:
            raise NotSavedError("Class must be saved before being able to get an user")
        
        status, user_info = wclass._api.getuser(wclass.qclass, wclass.rclass, quser, verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(user_info['message'])
        status, user_password = wclass._api.getuser(wclass.qclass, wclass.rclass, quser,
                                                    ["password"], verbose=True)
        if not status:  # pragma: no cover
            raise AdmRawError(user_password['message'])
        
        user_info['password'] = user_password['password']
        user = User(quser, **user_info)
        user._class = wclass
        user.wclass = True
        return user
    
    
    @classmethod
    def list(cls, wclass):
        return [cls.get(wclass, quser) for quser in wclass.infos["userlist"]]
