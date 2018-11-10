from wimsapi.exceptions import AdmRawException



class User():
    
    def __init__(self, quser, lastname, firstname, password, email="", comments="", regnum="",
                 photourl="", participate="", courses="", classes="", supervise="",
                 supervisable="no",
                 external_auth="", agreecgu="yes", regprop1="", regprop2="", regprop3="",
                 regprop4="", regprop5="", **kwargs):
        self._class = None
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
        return (self.firstname + " " + self.firstname).title()
    
    @property
    def infos(self):
        status, user_info = self._api.getuser(
                self._class.qclass, self._class.qclass.rclass, self.quser)
        if not status:
            raise AdmRawException(user_info['message'])
        
        for k in ['status', 'code', 'job']:
            del user_info[k]
        return user_info
    
    
    def _to_payload(self):
        return {k: v for k, v in self.__dict__.items() if k not in ['quser', '_api', '_class']}
    
    
    def save(self):
        if not self._class:
            raise ValueError("User must be added to a Wims class before being saved. Use "
                             "Class.adduser() to add an user to a Wims class.")
        
        status, response = self._class._api.moduser(
                self._class.qclass, self._class.rclass, self.quser, self._to_payload())
        
        if not status:
            raise AdmRawException(response['message'])
