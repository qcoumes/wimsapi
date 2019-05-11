"""Low-level API of the adm/raw module of WIMS.

For higher level classes like Class, User and Sheet, see the other .py files.

WIMS direct communication with another web server is two-directional. It can
receive http/https requests from the other server, and/or send http/https
requests to the other.

The connectable server must be declared in a file
within the directory 'WIMS_HOME/log/classes/.connections/'.

Warning: output must be set 'ident_type=json' and agent must be set to
'ident_agent=python-requests' in 'WIMS_HOME/log/classes/.connections/IDENT' for
this API to work properly.

For more informations, see http://wims.unice.fr/wims/?module=adm/raw&job=help"""

import json
import random
import string

import requests



def random_code():
    """Returns a random code for an adm/raw request."""
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))



def parse_response(request, verbose=False, return_request=False):
    """Return a dictionnary containing at least 'status' and 'message' keys.
    
    The goal is that the response is always the same, whether the output type of the WIMS server is
    set to JSON or WIMS.
    
    Warning: output must be set 'ident_type=json' in 'WIMS_HOME/log/classes/.connections/IDENT'
    for this API to work properly."""
    try:
        response = request.json()
    except json.JSONDecodeError:
        status, message = request.text.split('\n', maxsplit=1)
        code = "N/A"
        if ' ' in status:
            status, code = status.split(' ', maxsplit=1)
        response = {
            'status':  status,
            'message': message if '\n' not in message else message[:-1],
            'code':    code,
        }
    if response['status'] not in ["ERROR", "OK"]:
        if not return_request:  # pragma: no cover
            if not verbose:
                msg = ("Use verbose=True to see the received response content "
                       + "or use return_request=True to get the request object.")
            else:
                msg = "Received:\n\n" + request.text
            raise ValueError("Not a adm/raw response, maybe the URL is incorrect. " + msg)
        return request
    
    return response



class WimsAPI:
    """This class allow a python3 script to communicate with a WIMS server.
    
    Parameters:
        url - (str) url to the wims server CGI. e.g. https://wims.unice.fr/wims/wims.cgi
        ident - (str) Sender identifier (a word, according to the definition
                in WIMS_HOME/log/classes/.connections/)
        passwd - (str) Sender password (as defined in WIMS_HOME/log/classes/.connections/)
    
    
    Two optionnal parameter can be passed to every method:
        code - (str) a word sent to the request. A random code will be created by the method if none
               is provided. This word will be sent back, in order to allow to check whether the
               result is from the good request.
        verbose - (boolean) Default to False. Tell whether or not showing the whole response in the
                   the exception if the response could not be parsed.
    Any additionnal keyword argument will be passe to the request.post() function.
    
    Every method return a tuple containing a boolean and a dictionnary containing at least 'status',
    'message' and 'code' keys.
    Status is either a word OK (which set the boolean to True), or the word ERROR (which set the
    boolean to False).
    In case the status is OK, the 'message' key contains the remaining of the data (can be empty),
    the dictionnary can also contains more keys.
    In case the status is ERROR, key 'message' contains the nature of the error.
    
    Warning: output must be set 'ident_type=json' in 'WIMS_HOME/log/classes/.connections/IDENT'
    for this API to work properly.
    
    For more informations, see http://wims.unice.fr/wims/?module=adm/raw&job=help"""
    
    
    def __init__(self, url, ident, passwd):
        self.params = {'module': 'adm/raw', 'ident': ident, 'passwd': passwd}
        self.url = url
    
    
    @property
    def ident(self):
        """Returns the ident used by this instance of WimsAPI."""
        return self.params['ident']
    
    
    @property
    def passwd(self):
        """Returns the passwd used by this instance of WimsAPI."""
        return self.params['passwd']
    
    
    def addclass(self, rclass, class_info, supervisor_info, qclass=None, verbose=False, code=None,
                 **kwargs):
        """Add a class on the receiving server.
        
        if provided, qclass will be the identifier of the newly created WIMS class. The identifier
        is randomly chosen if qclass is not provided.
        
        Parameters:
            rclass - (str) identifier of the class on the sending server.
            class_info - (dict) properties of the new class, following keys may be present:
                Mandatory:
                    description - (str) name of the class
                    institution - (str) name of the institution
                    supervisor - (str) full name of the supervisor
                    email - (str) contact email address
                    password - (str) password for user registration
                    lang - (str) class language (en, fr, es, it, etc)
                Optionnal:
                    expiration - (str) class expiration date (yyyymmdd, defaults to one year later)
                    limit - (str) limit of number of participants (defaults to 30)
                    level - (str) level of the class (defaults to H4) Valid levels: E1,
                                      E2, ..., E6, H1, ..., H6, U1, ..., U5, G, R
                    secure - (str) secure hosts
                    bgcolor - (str) page background color
                    refcolor - (str) menu background color
                    css - (str) css file (must be existing css on the WIMS server)
            supervisor_info - (dict) properties of the supervisor account, folowing keys may be
                              present:
                Mandatory
                    lastname - (str) last name of the supervisor user
                    firstname - (str) first name of the supervisor user
                    password - (str) user's password, non-crypted.
                Optionnal:
                    email - (str) supervisor email address
                    comments - (str) any comments
                    regnum - (str) registration number
                    photourl - (str) url of an user picture
                    participate - (str) list classes (if in a class group) where user participates
                    agreecgu - (str) Boolean indicating if user accepted CGU
                    regprop1, regprop2, ... regprop5 - (str) custom properties
            qclass - (int) if provided, identifier of the newly created WIMS class. The identifier
                           is randomly chosen if not provided."""
        params = {
            **self.params,
            **{
                'job':    'addclass',
                'code':   code if code else random_code(),
                'rclass': rclass,
                'data1':  '\n'.join([str(k) + "=" + str(v) for k, v in class_info.items()]),
                'data2':  '\n'.join([str(k) + "=" + str(v) for k, v in supervisor_info.items()]),
            },
            **({'qclass': qclass} if qclass is not None else {})
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def addexam(self, qclass, rclass, exam_info, verbose=False, code=None, **kwargs):
        """Add an exam to the specified class.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            exam_info - (dict) properties of the exam, following keys may be present:
                title - (str) title of the exam
                description - (str) description of the exam
                expiration - (str) exam expiration date (yyyymmdd)
                duration - (int) duration (in minutes)
                attempts - (int) number of attempts"""
        params = {
            **self.params,
            **{
                'job':    'addexam',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'data1':  '\n'.join([str(k) + "=" + str(v) for k, v in exam_info.items()]),
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def addexo(self, qclass, rclass, qexo, exo_src, no_build=False, verbose=False, code=None,
               **kwargs):
        """Add an exercice to the specified class.
        
        Parameters:
            qclass  - (int) identifier of the class on the receiving server.
            rclass  - (str) identifier of the class on the sending server.
            qexo    - (str) exo identifier on the receiving server.
            exo_src - (str) source of the exercice.
            no_build - (bool) Do not compile the exercise. Improves the speed when there is a lot
                              of exercices to handle at the same time. Do not forget to call
                              buildexos() to compile them at the end (defaults to False)"""
        params = {
            **self.params,
            **{
                'job':    'addexo',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qexo':   qexo,
                'data1':  exo_src,
            }
        }
        if no_build:
            params['option'] = 'no_build'
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def addsheet(self, qclass, rclass, sheet_info, verbose=False, code=None, **kwargs):
        """Add a sheet to the specified class.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            sheet_info - (dict) properties of the sheet, following keys may be present:
                Mandatory:
                    /
                Optionnal:
                    title - (str) name of the sheet (defaults to "sheet n#")
                    description - (str) description of the sheet (defaults to "sheet n#")
                    expiration - (str) expiration date (yyyymmdd) defaults to one year later
                    sheetmode - (str) the mode of the sheet:
                        0 : pending (default)
                        1 : active
                        2 : expired
                        3 : expired + hidden
                    weight - (int) weight of the sheet in the class score (default to 1), use 0 if
                        you want this sheet's score to be ignored.
                    formula - (str) How the score is calculated for this sheet (0 to 6,
                                    default to 2)
                        0 : Very lenient: maximum between percentage and quality.
                        1 : Quality is not taken into account. You get maximum of
                            grade once all the required work is done.
                        2 : Quality has only slight effect over the grade.
                        3 : More effect of quality.
                        4 : To have a grade of 10, you must gather all require
                            points (100%) without making any error (quality=10).
                        5 : Unfinished work is over-punished.
                        6 : Any mistake is over-punished.
                    indicator - (str) what indicator will be used in the score formula (0 to 2,
                        default to 1)
                    contents - (str) the contents for the multi-line file to be created.
                        The semicolons (;) in this parameter will be
                        interpreted as new lines. Equal characters (=) must
                        be replaced by the character AT (@).
                        There is no check made, so the integrity of the
                        contents is up to you only! (defaults to "")"""
        params = {
            **self.params,
            **{
                'job':    'addsheet',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'data1':  '\n'.join([str(k) + "=" + str(v) for k, v in sheet_info.items()]),
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def adduser(self, qclass, rclass, quser, user_info, verbose=False, code=None, **kwargs):
        """Add an user to the specified class.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server.
            user_info - (dict) properties of the user, following keys may be present:
                Mandatory
                    lastname - (str) last name of the user
                    firstname - (str) first name of the user
                    password - (str) user's password, non-crypted.
                Optionnal:
                    email - (str) email address
                    comments - (str) any comments
                    regnum - (str) registration number
                    photourl - (str) url of user's photo
                    participate - (str) list classes where user participates
                    courses - (str) special for portal
                    classes - (str) special for portal
                    supervise - (str) List classes where teacher are administator
                    supervisable - (str) yes/no ; give right to the user to supervise a class
                    external_auth - (str) login for external_auth
                    agreecgu - (str) if yes, the user will not be asked when he enters
                               for the first time to agree the cgu
                    regprop[1..5] - (str) custom variables"""
        params = {
            **self.params,
            **{
                'job':    'adduser',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'quser':  quser,
                'data1':  '\n'.join([str(k) + "=" + str(v) for k, v in user_info.items()]),
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def authuser(self, qclass, rclass, quser, hashlogin=None, verbose=False, code=None, **kwargs):
        """Get an authentification token for an user.
        
        User's password is not required.
        
        If parameter hashlogin is set to an hash function name, quser should be the external
        identification of user and the function hashlogin is called to convert
        such id to a WIMS login. If the user exists in class, it returns a
        session number as above. If the user does not exists, the WIMS login is
        returned in the error message.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server.
            hashlogin  - (str) hash function to use for an external authentification
            
        Return a session number under which the user can connect with no need of further
        authentification"""
        params = {
            **self.params,
            **{
                'job':    'authuser',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'quser':  quser,
            }
        }
        if hashlogin:
            params['hashlogin'] = hashlogin
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def buildexos(self, qclass, rclass, verbose=False, code=None, **kwargs):
        """Compile every exercises of the specified class.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server."""
        params = {
            **self.params,
            **{
                'job':    'buildexos',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def checkclass(self, qclass, rclass, verbose=False, code=None, **kwargs):
        """Check whether the class accepts connection.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server."""
        params = {
            **self.params,
            **{
                'job':    'checkclass',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def checkexam(self, qclass, rclass, qexam, verbose=False, code=None, **kwargs):
        """Check whether the exam exists.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qexam  - (str) exam identifier on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'checkexam',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qexam':  qexam,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def checkident(self, verbose=False, code=None, **kwargs):
        """Check whether the connection is accepted."""
        params = {
            **self.params,
            **{'job': 'checkident', 'code': code if code else random_code()}
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def checksheet(self, qclass, rclass, qsheet, verbose=False, code=None, **kwargs):
        """Check whether the sheet exists.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (str) identifier of the sheet on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'checksheet',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def checkuser(self, qclass, rclass, quser, verbose=False, code=None, **kwargs):
        """Check whether the user exists.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'checkuser',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'quser':  quser,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def cleanclass(self, qclass, rclass, verbose=False, code=None, **kwargs):
        """Delete users (but supervisor) and all work done by students on the specified class.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server."""
        params = {
            **self.params,
            **{
                'job':    'cleanclass',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def copyclass(self, qclass, rclass, verbose=False, code=None, **kwargs):
        """Copy a class. Do not copy users or work done by students.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server."""
        params = {
            **self.params,
            **{
                'job':    'copyclass',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def delclass(self, qclass, rclass, verbose=False, code=None, **kwargs):
        """Delete a class.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server."""
        params = {
            **self.params,
            **{
                'job':    'delclass',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def delexam(self, qclass, rclass, qexam, verbose=False, code=None, **kwargs):
        """Delete an exam.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qexam   - (str) exam identifier on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'delexam',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qexam':  qexam,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def delexo(self, qclass, rclass, qexo, verbose=False, code=None, **kwargs):
        """Delete an exo.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qexo   - (str) exo identifier on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'delexo',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qexo':   qexo,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def delsheet(self, qclass, rclass, qsheet, verbose=False, code=None, **kwargs):
        """Delete a sheet
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (int) identifier of the sheet on the receiving server.
            options - (list) names of fields queried."""
        params = {
            **self.params,
            **{
                'job':    'delsheet',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def deluser(self, qclass, rclass, quser, verbose=False, code=None, **kwargs):
        """Delete an user.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'deluser',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'quser':  quser,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getclass(self, qclass, rclass, options=None, verbose=False, code=None, **kwargs):
        """Get the properties of a class.
        
        Optionally, the parameter 'options' may contain the names of fields
        queried. In this case, only the queried properties are returned.
        
        Existing properties are: password, creator, secure, external_auth, mixed_external_auth,
        cas_auth, php_auth, authidp, supervisor, description, institution, lang, email, expiration,
        limit, topscores, superclass, type, level, parent, typename, bgcolor, bgimg, scorecolor,
        css, logo, logoside, refcolor, ref_menucolor, ref_button_color, ref_button_bgcolor,
        ref_button_help_color, ref_button_help_bgcolor, theme, theme_icon, connections, creation,
        userlist, usercount, examcount, sheetcount
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            options - (list) names of fields queried."""
        params = {
            **self.params,
            **{
                'job':    'getclass',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
            }
        }
        if options:
            params['option'] = ','.join(options)
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getclassesuser(self, rclass, quser, verbose=False, code=None, **kwargs):
        """List all the classes having connection with rclass where quser exists.
        
        Optionally, the parameter 'options' may contain the names of fields
        queried for each class. In this case, only the queried properties are returned.
        
        Existing properties are: password, creator, secure, external_auth, mixed_external_auth,
        cas_auth, php_auth, authidp, supervisor, description, institution, lang, email, expiration,
        limit, topscores, superclass, type, level, parent, typename, bgcolor, bgimg, scorecolor,
        css, logo, logoside, refcolor, ref_menucolor, ref_button_color, ref_button_bgcolor,
        ref_button_help_color, ref_button_help_bgcolor, theme, theme_icon, connections, creation,
        userlist, usercount, examcount, sheetcount
        
        Parameters:
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server.
            options - (list) names of fields queried."""
        params = {
            **self.params,
            **{
                'job':    'getclassesuser',
                'code':   code if code else random_code(),
                'rclass': rclass,
                'quser':  quser,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getclassfile(self, qclass, rclass, filename, code=None, **kwargs):
        """Download the file <filename> of the specified class.
        
        Parameters:
            qclass - (str) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            filename - (str) path to the file relative to 'log/classes/[qclass]/'.
            """
        params = {
            **self.params,
            **{
                'job':    'getclassfile',
                'code':   code if code else random_code(),
                'rclass': rclass,
                'qclass': qclass,
                'option': filename,
            }
        }
        request = requests.post(self.url, params=params, stream=True, **kwargs)
        response = parse_response(request, return_request=True)
        return (
            response['status'] == 'OK' if isinstance(response, dict) else True,
            response if isinstance(response, dict) else request.content
        )
    
    
    def getclassmodif(self, qclass, rclass, date, verbose=False, code=None, **kwargs):
        """List all the files modified on the specified class since <date>.
        
        Parameters:
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server.
            date   - (str) date (yyyymmdd)"""
        params = {
            **self.params,
            **{
                'job':    'getclassmodif',
                'code':   code if code else random_code(),
                'rclass': rclass,
                'qclass': qclass,
                'data1':  date,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getclasstgz(self, qclass, rclass, code=None, **kwargs):
        """Download the class in a compressed (tar-gzip) file.
        
        Parameters:
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'getclasstgz',
                'code':   code if code else random_code(),
                'rclass': rclass,
                'qclass': qclass,
            }
        }
        request = requests.post(self.url, params=params, stream=True, **kwargs)
        response = parse_response(request, return_request=True)
        return (
            response['status'] == 'OK' if isinstance(response, dict) else True,
            response if isinstance(response, dict) else request.content
        )
    
    
    def getcsv(self, qclass, rclass, options, frmt='csv', code=None, **kwargs):
        """Get data of the class, under the form of a csv/tsv/xls spreatsheet file.
        
        The parameter 'frmt' may be used to specify the desired output frmt
        (csv or tsv, defaults to csv).
        
        The parameter 'options' should contain a list of desired data columns.
        The following names can be included in 'option', with their respective meanings:
            login       : user identifiers
            password    : user passwords (uncrypted)
            name        : user names (last name and first name)
            lastname    : user family names
            firstname   : user given names
            email       : user email addresses
            regnum      : user registration numbers
            allscore    : all score fields (averages and details)
            averages    : score averages (average0, average1, average2)
            average0    : global score average (as computed by WIMS)
            average1    : average of scores automatically attributed by WIMS
            average2    : average of teacher-entered scores
            exams       : exam1+exam2+...
            exam1, exam2, ...: scores of each exam
            sheets      : sheet1+sheet2+...
            sheet1, sheet2, ...: scores of each worksheet
            manuals     : manual1+manual2+...
            manual1, manual2, ...: first, second, ... teacher-entered scores.

        The output content (below the status line in WIMS frmt) is a csv/tsv
        spreadsheet table. The first row of the table contains
        the names of the fields. The second row gives short
        descriptions of each field. The third row is blank.
        The rest is the table content, with one row for each user.
        
        Parameters:
            qclass  - (int) identifier of the class on the receiving server.
            rclass  - (str) identifier of the class on the sending server.
            options - (list) list of desired data columns.
            frmt  - (str) output frmt ('csv', 'tsv' or 'xls', defaults to csv)"""
        params = {
            **self.params,
            **{
                'job':    'getcsv',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'frmt':   frmt,
            }
        }
        if options:
            params['option'] = ','.join(options)
        request = requests.post(self.url, params=params, stream=True, **kwargs)
        response = parse_response(request, return_request=True)
        return (
            response['status'] == 'OK' if isinstance(response, dict) else True,
            response if isinstance(response, dict) else request.content
        )
    
    
    def getexam(self, qclass, rclass, qexam, verbose=False, code=None, **kwargs):
        """Get an exam from a class.
        
         Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qexam  - (int) identifier of the exam on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'getexam',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qexam':  qexam,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getexamlog(self, qclass, rclass, quser, qexam, verbose=False, code=None, **kwargs):
        """Get the logs of <quser> on <qexam> inside of a class.
        
         Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            quser  - (int) identifier of the user on the receiving server.
            qexam  - (int) identifier of the exam on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'getexamlog',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'quser':  quser,
                'qexam':  qexam,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getexamscores(self, qclass, rclass, qexam, verbose=False, code=None, **kwargs):
        """Get all scores from exam.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qexam  - (int) identifier of the exam on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'getexamscores',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qexam':  qexam,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getexo(self, qclass, rclass, qsheet, qexo, verbose=False, code=None, **kwargs):
        """Get an exercice from a sheet.
        
         Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (int) identifier of the sheet on the receiving server.
            qexo   - (int) identifier of the exo on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'getexo',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
                'qexo':   qexo,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getexofile(self, qclass, rclass, qexo, code=None, **kwargs):
        """Download the <qexo> source file of the specified class.
        
         Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qexo   - (int) identifier of the exo on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'getexofile',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qexo':   qexo,
            }
        }
        request = requests.post(self.url, params=params, stream=True, **kwargs)
        response = parse_response(request, return_request=True)
        return (
            response['status'] == 'OK' if isinstance(response, dict) else True,
            response if isinstance(response, dict) else request.content
        )
    
    
    def getexosheet(self, qclass, rclass, qsheet, qexo, verbose=False, code=None, **kwargs):
        """Get informations of <qexo> inside of <qsheet> of the specified class.
        
         Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (int) identifier of the sheet on the receiving server.
            qexo   - (int) identifier of the exo on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'getexosheet',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
                'qexo':   qexo,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getinfoserver(self, verbose=False, code=None, **kwargs):
        """Get informations about the WIMS server."""
        params = {
            **self.params,
            **{
                'job':  'getinfoserver',
                'code': code if code else random_code(),
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getlog(self, qclass, rclass, quser, verbose=False, code=None, **kwargs):
        """Get the detailed activity registry of an user.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'getlog',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'quser':  quser,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getmodule(self, module, verbose=False, code=None, **kwargs):
        """Get informations about <module>.
        
        Parameters:
            module - (str) path of a module (i.e. 'E1/geometry/oefsquare.fr')"""
        params = {
            **self.params,
            **{
                'job':    'getmodule',
                'code':   code if code else random_code(),
                'option': module,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getscore(self, qclass, rclass, quser, qsheet=None, verbose=False, code=None, **kwargs):
        """Get all scores from user.
        
        Can optionnal filter from a sheet.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server.
            qsheet - (int) identifier of the sheet on the receiving server.
                           Used to filter the scores."""
        params = {
            **self.params,
            **{
                'job':    'getscore',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'quser':  quser,
            }
        }
        if qsheet is not None:
            params['qsheet'] = qsheet
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getscores(self, qclass, rclass, options, code=None, **kwargs):
        """Call getcsv() method with format='xls'.
        
        For more informations, see WimsAPI.getcsv() documentation."""
        return self.getcsv(qclass, rclass, options, frmt='xls', code=code,
                           **kwargs)
    
    
    def getsession(self, data1='adm/createxo', verbose=False, code=None, **kwargs):
        """Open a WIMS session and return its ID"""
        params = {
            **self.params,
            **{
                'job':   'getsession',
                'code':  code if code else random_code(),
                'data1': data1,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getsheet(self, qclass, rclass, qsheet, options=None, verbose=False, code=None, **kwargs):
        """Get the properties of a sheet (of a class).
        
        Optionally, the parameter 'options' may contain the names of fields
        queried. In this case, only the queried properties are returned.
        
        Existing properties are: exo_cnt, sheet_properties, sheet_status, sheet_expiration,
        sheet_title, sheet_description, exolist, title, params, points, weight, description
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (int) identifier of the sheet on the receiving server.
            options - (list) names of fields queried."""
        params = {
            **self.params,
            **{
                'job':    'getsheet',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
            }
        }
        if options:
            params['option'] = ','.join(options)
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getsheetscores(self, qclass, rclass, qsheet, verbose=False, code=None, **kwargs):
        """Get all scores from sheet.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (int) identifier of the sheet on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'getsheetscores',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getsheetstats(self, qclass, rclass, qsheet, verbose=False, code=None, **kwargs):
        """Get stats about work of students for every exercise of <qsheet>.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (int) identifier of the sheet on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'getsheetstats',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def gettime(self, verbose=False, code=None, **kwargs):
        """Get the current time of the server.
        
        Can be used for synchronization purposes."""
        params = {
            **self.params,
            **{
                'job':  'gettime',
                'code': code if code else random_code(),
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def getuser(self, qclass, rclass, quser, options=None, verbose=False, code=None, **kwargs):
        """Get the properties of an user (of a class).
        
        Optionally, the parameter 'options' may contain the names of fields
        queried. In this case, only the queried properties are returned.
        
        Existing properties are: firstname, lastname, email, comments, regnum, photourl,
        participate, password, courses, classes, supervise, supervisable, external_auth,
        agreecgu, regprop1, regprop2, regprop3, regprop4, regprop5
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server.
            options - (list) names of fields queried."""
        params = {
            **self.params,
            **{
                'job':    'getuser',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'quser':  quser,
            }
        }
        if options:
            params['option'] = ','.join(options)
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def lightpopup(self, qclass, rclass, quser, session, exercice, about=True, code=None, **kwargs):
        """Presents an exercise without the top, bottom, and left menu

        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server.
            session - (str) session identifer returned by authuser().
            exercice - (str) addresse of the exercice found in 'About this module / this exercice'
                       on the page of the exercice eg:
                       'classes/en&exo=Exercise1&qnum=1&qcmlevel=1&scoredelay=700,700 '
            about - (bool) If True (default), show "about" which gives author information about the
                     exercise"""
        params = {
            **self.params,
            **{
                'job':     'lightpopup',
                'code':    code if code else random_code(),
                'qclass':  qclass,
                'rclass':  rclass,
                'quser':   quser,
                'session': session,
                'emod':    exercice,
                'option':  'about' if about else 'noabout',
            }
        }
        request = requests.post(self.url, params=params, stream=True, **kwargs)
        response = parse_response(request, return_request=True)
        return (
            response['status'] == 'OK' if isinstance(response, dict) else True,
            response if isinstance(response, dict) else request.content
        )
    
    
    def linkexo(self, qclass, rclass, qsheet, qexo, qexam, verbose=False, code=None, **kwargs):
        """Add exercise <qexo> of the sheet <qsheet> to <qexam>.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (int) identifier of the sheet on the receiving server.
            qexam - (int) identifier of the exam on the receiving server.
        """
        params = {
            **self.params,
            **{
                'job':    'linkexo',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
                'qexo':   qexo,
                'qexam':  qexam,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def linksheet(self, qclass, rclass, qsheet, qexam, verbose=False, code=None, **kwargs):
        """Add all exercices from sheet to exam.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (int) identifier of the sheet on the receiving server.
            qexam - (int) identifier of the exam on the receiving server.
        """
        params = {
            **self.params,
            **{
                'job':    'linksheet',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
                'qexam':  qexam,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def listclasses(self, rclass, verbose=False, code=None, **kwargs):
        """List all the classes having connection with rclass.
        
        Optionally, the parameter 'options' may contain the names of fields
        queried for each class. In this case, only the queried properties are returned.
        
        Existing properties are: password, creator, secure, external_auth, mixed_external_auth,
        cas_auth, php_auth, authidp, supervisor, description, institution, lang, email, expiration,
        limit, topscores, superclass, type, level, parent, typename, bgcolor, bgimg, scorecolor,
        css, logo, logoside, refcolor, ref_menucolor, ref_button_color, ref_button_bgcolor,
        ref_button_help_color, ref_button_help_bgcolor, theme, theme_icon, connections, creation,
        userlist, usercount, examcount, sheetcount
        
        Parameters:
            rclass - (str) identifier of the class on the sending server.
            options - (list) names of fields queried."""
        params = {
            **self.params,
            **{
                'job':    'listclasses',
                'code':   code if code else random_code(),
                'rclass': rclass,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def listexams(self, qclass, rclass, verbose=False, code=None, **kwargs):
        """Lists all exams presents in class.

        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server."""
        params = {
            **self.params,
            **{
                'job':    'listexams',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def listexos(self, qclass, rclass, verbose=False, code=None, **kwargs):
        """Lists all exercices presents in class.

        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server."""
        params = {
            **self.params,
            **{
                'job':    'listexos',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def listlinks(self, qclass, rclass, qsheet, qexam, verbose=False, code=None, **kwargs):
        """Get the number of exercise of <qsheet> linked to <qexam>.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (int) identifier of the sheet on the receiving server.
            qexam - (int) identifier of the exam on the receiving server.
        """
        params = {
            **self.params,
            **{
                'job':    'listlinks',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
                'qexam':  qexam,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def listmodules(self, level='H4', verbose=False, code=None, **kwargs):
        """Get the number of exercise of <qsheet> linked to <qexam>.
        
        Parameters:
            level - (str) level of the module (defaults to H4).
                          Valid levels are E1, E2, ..., E6, H1, ..., H6, U1, ..., U5, G, R
        """
        params = {
            **self.params,
            **{
                'job':    'listmodules',
                'code':   code if code else random_code(),
                'option': level,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def listsheets(self, qclass, rclass, verbose=False, code=None, **kwargs):
        """List all the sheets of a class.

        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server."""
        params = {
            **self.params,
            **{
                'job':    'listsheets',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def modclass(self, qclass, rclass, class_info, verbose=False, code=None, **kwargs):
        """Modify the properties of a class.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            class_info - (dict) Only modified properties need to be present, following keys
                         may be present:
                description - (str) name of the class
                institution - (str) name of the institution
                supervisor - (str) full name of the supervisor
                email - (str) contact email address
                password - (str) password for user registration
                lang - (str) class language (en, fr, es, it, etc)
                expiration - (str) class expiration date (yyyymmdd, defaults to one year later)
                limit - (str) limit of number of participants (defaults to 30)
                level - (str) level of the class (defaults to H4) Valid levels: E1,
                                  E2, ..., E6, H1, ..., H6, U1, ..., U5, G, R
                secure - (str) secure hosts
                bgcolor - (str) page background color
                refcolor - (str) menu background color
                css - (str) css file (must be existing css on the WIMS server)"""
        params = {
            **self.params,
            **{
                'job':    'modclass',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'data1':  '\n'.join([str(k) + "=" + str(v) for k, v in class_info.items()]),
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def modexam(self, qclass, rclass, qexam, exam_info, verbose=False, code=None, **kwargs):
        """Modify the property of an exam.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            exam_info - (dict) Only modified properties need to be present, following keys
                         may be present:
                title - (str) title of the exam
                description - (str) description of the exam
                expiration - (str) exam expiration date (yyyymmdd)
                duration - (int) duration (in minutes)
                attempts - (int) number of attempts"""
        params = {
            **self.params,
            **{
                'job':    'modexam',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qexam':  qexam,
                'data1':  '\n'.join([str(k) + "=" + str(v) for k, v in exam_info.items()]),
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def modexosheet(self, verbose=False, code=None, **kwargs):
        """Not yet implemented."""
        pass  # TODO
    
    
    def modsheet(self, qclass, rclass, qsheet, sheet_info, verbose=False, code=None, **kwargs):
        """Modify the properties of a sheet.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (int) identifier of the sheet on the receiving server.
            sheet_info - (dict) Only modified properties need to be present, following keys
                         may be present:
                title - (str) name of the sheet (defaults to "sheet n#")
                description - (str) description of the sheet (defaults to "sheet n#")
                expiration - (str) expiration date (yyyymmdd) defaults to one year later
                status - (str) the mode of the sheet:
                                0 : pending (default)
                                1 : active
                                2 : expired
                                3 : expired + hidden
                weight - (str) weight of the sheet in class score
                formula - (str) How the score is calculated for this sheet (0 to 6)
                indicator - (str) what indicator will be used in the score formula (0 to 2)
                contents - (str) the contents for the multi-line file to be created.
                              The semicolons (;) in this parameter will be
                              interpreted as new lines. Equal characters (=) must
                              be replaced by the character AT (@).
                              There is no check made, so the integrity of the
                              contents is up to you only! (defaults to "")"""
        params = {
            **self.params,
            **{
                'job':    'modsheet',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
                'data1':  '\n'.join([str(k) + "=" + str(v) for k, v in sheet_info.items()]),
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def moduser(self, qclass, rclass, quser, user_info, verbose=False, code=None, **kwargs):
        """Modify the properties of an user.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server.
            user_info - (dict) Only modified properties need to be present, following keys
                         may be present:
                lastname - (str) last name of the supervisor user
                firstname - (str) first name of the supervisor user
                password - (str) user's password, non-crypted.
                email - (str) email address
                comments - (str) any comments
                regnum - (str) registration number
                photourl - (str) url of user's photo
                participate - (str) list classes where user participates
                courses - (str) special for portal
                classes - (str) special for portal
                supervise - (str) List classes where teacher are administator
                supervisable - (str) yes/no ; give right to the user to supervise a class
                external_auth - (str) login for external_auth
                agreecgu - (str) if yes, the user will not be asked when he enters
                           for the first time to agree the cgu
                regprop[1..5] - (str) custom variables"""
        params = {
            **self.params,
            **{
                'job':    'moduser',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'quser':  quser,
                'data1':  '\n'.join([str(k) + "=" + str(v) for k, v in user_info.items()]),
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def movexo(self, qclass, qclass2, rclass, qsheet, copy=False, verbose=False, code=None,
               **kwargs):
        """Moves exercice from qclass to qclass2.
        
        Condition : Both 2 classes must be linked by.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server, source of the exo.
            qclass2 - (int) identifier of the class on the receiving server, destination of the exo.
            rclass - (str) identifier of the class on the sending server.
            qsheet - (int) identifier of the sheet on the receiving server.
            copy - (bool) If set to True, copy the exo instead of moving it.
        """
        params = {
            **self.params,
            **{
                'job':    'movexo',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
                'data1':  qclass2,
            }
        }
        if copy:
            params['option'] = 'copy'
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def movexos(self, qclass, qclass2, rclass, copy=False, verbose=False, code=None, **kwargs):
        """Moves ALL exercices from qclass to qclass2.
        
        Condition : Both 2 classes must be linked by.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server, source of the exos.
            qclass2 - (int) identifier of the class on the receiving server, destination of the exo.
            rclass - (str) identifier of the class on the sending server.
            copy - (bool) If set to True, copy the exo instead of moving it.
        """
        params = {
            **self.params,
            **{
                'job':    'movexos',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'data1':  qclass2,
            }
        }
        if copy:
            params['option'] = 'copy'
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def putcsv(self, qclass, rclass, csv, file=True, verbose=False, code=None, **kwargs):
        """Put data into the class.
        
        csv should respect this format: The first row of the table contains
        the names of the fields. The second row gives short
        descriptions of each field. The second row is blank.
        The rest is the table content, with one row for each user.
        The following data columns can be included in the csv, with their respective meanings:
            login       : user identifiers
            password    : user passwords (uncrypted)
            name        : user names (last name and first name)
            lastname    : user family names
            firstname   : user given names
            email       : user email addresses
            regnum      : user registration numbers
            allscore    : all score fields (averages and details)
            averages    : score averages (average0, average1, average2)
            average0    : global score average (as computed by WIMS)
            average1    : average of scores automatically attributed by WIMS
            average2    : average of teacher-entered scores
            exams       : exam1+exam2+...
            exam1, exam2, ...: scores of each exam
            sheets      : sheet1+sheet2+...
            sheet1, sheet2, ...: scores of each worksheet
            manuals     : manual1+manual2+...
            manual1, manual2, ...: first, second, ... teacher-entered scores.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            csv	   - (str) path to a csv if 'file' is True (default), content of a csv otherwise.
            file   - (bool) Whether csv must be interpreted as a path to a csv or a .csv string"""
        if file:
            with open(csv) as f:
                csv = f.read()
        params = {
            **self.params,
            **{
                'job':    'putcsv',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'data1':  csv,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def putexo(self, qclass, rclass, qsheet, module, options=None, verbose=False, code=None,
               **kwargs):
        """Add <module>'s exercise to <qsheet> of a specified class.
        
        Parameters:
            qclass  - (int) identifier of the class on the receiving server.
            rclass  - (str) identifier of the class on the sending server.
            qsheet  - (str) sheet identifier on the receiving server.
            module  - (str) path of a module (i.e. 'E1/geometry/oefsquare.fr').
            options - (dict) A dictionnary of optionnal parameters:
                params - (str) string of parameters to add to the module.
                points - (int) number of requested points.
                weight - (int) weight of the exercise.
                title  - (str) title of the exercise in the sheet.
                description  - (str) description of the exercise in the sheet."""
        
        params = {
            **self.params,
            **{
                'job':    'putexo',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'qsheet': qsheet,
                'data1':  'module=' + module,
            }
        }
        if options:
            params['data1'] += ('\nparams='
                                + '\n'.join([str(k) + "=" + str(v) for k, v in options.items()]))
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def recuser(self, qclass, rclass, quser, verbose=False, code=None, **kwargs):
        """Recover a deleted user.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            quser  - (str) user identifier on the receiving server."""
        params = {
            **self.params,
            **{
                'job':    'recuser',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'quser':  quser,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def repairclass(self, qclass, rclass, verbose=False, code=None, **kwargs):
        """Try to detect and correct eventual problems.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            rclass - (str) identifier of the class on the sending server."""
        params = {
            **self.params,
            **{
                'job':    'repairclass',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def search(self, verbose=False, code=None, **kwargs):
        """Not yet implemented."""
        pass  # TODO
    
    
    def sharecontent(self, qclass, qclass2, rclass, options=('exo',), verbose=False, code=None,
                     **kwargs):
        """Declares neighbour classes, allowing class "qclass" to share content with class "data1".
        
        Condition : Both 2 classes must be linked by.
        
        Parameters:
            qclass - (int) identifier of the class on the receiving server.
            qclass2 - (int) identifier of the second class on the receiving server.
            rclass - (str) identifier of the class on the sending server.
            options - (list) content to share (currently, only the "exo" content type is supported).
        """
        params = {
            **self.params,
            **{
                'job':    'sharecontent',
                'code':   code if code else random_code(),
                'qclass': qclass,
                'rclass': rclass,
                'option': ','.join(options),
                'data1':  qclass2,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def testexo(self, exo_src, verbose=False, code=None, **kwargs):
        """Allow to test the compilation of an exercise without adding it to a class.
        
        Parameters:
            exo_src - (str) source of the exercice."""
        params = {
            **self.params,
            **{
                'job':   'testexo',
                'code':  code if code else random_code(),
                'data1': exo_src,
            }
        }
        request = requests.post(self.url, data=params, **kwargs)
        response = parse_response(request, verbose)
        return response['status'] == 'OK', response
    
    
    def update(self, verbose=False, code=None, **kwargs):
        """Not yet implemented."""
        pass  # TODO
