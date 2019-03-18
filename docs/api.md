The main object-orientated API is built on top of *WimsAPI* class. Each
method on WimsAPI maps one-to-one with an *adm/raw* request, and returns
the response of the *WIMS* server.

It’s possible to use WimsAPI directly. Some basic things (e.g. getting
a class from server) consist of several API calls and are complex to do
with the low-level API, but it’s useful if you need extra flexibility
and power.


## `class WimsAPI`
**`WimsAPI(url, ident, passwd)`**

This class allow a python3 script to communicate with a WIMS server.
 
***Parameters:***

* url - (str) url to the wims server CGI. e.g. `https://wims.unice.fr/wims/wims.cgi`
* ident - (str) Sender identifier (a word, according to the definition
            in `WIMS_HOME/log/classes/.connections/`)
* passwd - (str) Sender password (as defined in `WIMS_HOME/log/classes/.connections/`)
 
 ___
 
Two optionnal parameter can be passed to every method of this class:

* code - (str) a word sent to the request. A random code will be created by the method if none
           is provided. This word will be sent back, in order to allow to check whether the
           result is from the good request.
* verbose - (boolean) Default to False. Tell whether or not showing the whole response in the
               the exception if the response could not be parsed.
* Any additionnal keyword argument will be passe to the `requests.post()` function.
 
___
 
Every method return a tuple `(boolean, dictionnary)`, where dictionnary contains at least
**status**, and **code** keys. **Status** is either the word **'OK'** (which set `boolean` to True),
or the word **'ERROR'** (which set `boolean` to False).

In case the status is **'OK'**, the dictionnary can contains additionnals keys corresponding to the
*adm/raw* response.
In case the status is **'ERROR'**, key **'message'** contains the nature of the error.

 
**/!\ Warning:** output must be set `ident_type=json` in `WIMS_HOME/log/classes/.connections/IDENT`
for this API to work properly. See [configuration](index.md)
 
For more informations about *adm/raw*, see http://wims.unice.fr/wims/?module=adm/raw&job=help

___

## `addclass`
**`addclass(self, qclass, rclass, class_info, supervisor_info, verbose=False, code=None, **kwargs)`**

Add a class on the receiving server.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* class_info - (dict) properties of the new class, following keys may be present:
    * Mandatory:
        * description - (str) name of the class
        * institution - (str) name of the institution
        * supervisor - (str) full name of the supervisor
        * email - (str) contact email address
        * password - (str) password for user registration
    * Optionnal:
        * expiration - (str) class expiration date (yyyymmdd, defaults to one year later)
        * limit - (str) limit of number of participants (defaults to 30)
        * level - (str) level of the class (defaults to H4) Valid levels: E1,
                        E2, ..., E6, H1, ..., H6, U1, ..., U5, G, R
        * secure - (str) secure hosts
        * bgcolor - (str) page background color
        * refcolor - (str) menu background color
        * css - (str) css file (must be existing css on the WIMS server)
        supervisor_info - (dict) properties of the supervisor account, folowing keys may be
        *           present:
            Mandatory
        * lastname - (str) last name of the supervisor user
        * firstname - (str) first name of the supervisor user
        * password - (str) user's password, non-crypted.
            Optionnal:
        * email - (str) supervisor email address
        * comments - (str) any comments
        * regnum - (str) registration number
        * photourl - (str) url of an user picture
        * participate - (str) list classes (if in a class group) where user participates
        * agreecgu - (str) Boolean indicating if user accepted CGU
        * regprop1, regprop2, ... regprop5 - (str) custom properties

___


## addexam
**`addexam(self, qclass, rclass, exam_info, verbose=False, code=None, **kwargs)`**

Add an exam to the specified class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* exam_info - (dict) properties of the exam, following keys may be present:
    * title - (str) title of the exam
    * description - (str) description of the exam
    * expiration - (str) exam expiration date (yyyymmdd)
    * duration - (int) duration (in minutes)
    * attempts - (int) number of attempts

## addexo
**`addexo(self, qclass, rclass, qexo, exo_src, no_build=False, verbose=False, code=None, **kwargs)`**

Add an exercice to the specified class.
     
***Parameters:***

* qclass  - (int) identifier of the class on the receiving server.
* rclass  - (str) identifier of the class on the sending server.
* qexo    - (str) exo identifier on the receiving server.
* exo_src - (str) source of the exercice.
* no_build - (bool) Do not compile the exercise. Improves the speed when there is a lot
                    of exercices to handle at the same time. Do not forget to call
                    buildexos() to compile them at the end (defaults to False)

## addsheet
**`addsheet(self, qclass, rclass, sheet_info, verbose=False, code=None, **kwargs)`**

Add a sheet to the specified class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* sheet_info - (dict) properties of the sheet, following keys may be present:
    *  title - (str) name of the sheet (defaults to "sheet n#")
    *  description - (str) description of the sheet (defaults to "sheet n#")
    *  expiration - (str) expiration date (yyyymmdd) defaults to one year later
    *  sheetmode - (str) the mode of the sheet. 0 : pending (default), 1 : active,
                         2 : expired, 3 : expired + hidden
    *  weight - (str) weight of the sheet in class score
    *  formula - (str) How the score is calculated for this sheet (0 to 6)
    *  indicator - (str) what indicator will be used in the score formula (0 to 2)
    *  contents - (str) the contents for the multi-line file to be created.
                        The semicolons (;) in this parameter will be
                        interpreted as new lines. Equal characters (=) must
                        be replaced by the character AT (@).
                        There is no check made, so the integrity of the
                        contents is up to you only! (defaults to "")

## adduser
**`adduser(self, qclass, rclass, quser, user_info, verbose=False, code=None, **kwargs)`**

Add an user to the specified class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.
* user_info - (dict) properties of the user, following keys may be present:
    * Mandatory
        *  lastname - (str) last name of the user
        *  firstname - (str) first name of the user
        *  password - (str) user's password, non-crypted.
    * Optionnal:
        *  email - (str) email address
        *  comments - (str) any comments
        *  regnum - (str) registration number
        *  photourl - (str) url of user's photo
        *  participate - (str) list classes where user participates
        *  courses - (str) special for portal
        *  classes - (str) special for portal
        *  supervise - (str) List classes where teacher are administator
        *  supervisable - (str) yes/no ; give right to the user to supervise a class
        *  external_auth - (str) login for external_auth
        *  agreecgu - (str) if yes, the user will not be asked when he enters
                        for the first time to agree the cgu
        *  regprop[1..5] - (str) custom variables

## authuser
**`authuser(self, qclass, rclass, quser, hashlogin=None, verbose=False, code=None, **kwargs)`**

Get an authentification token for an user.
 
User's password is not required.
 
If parameter hashlogin is set to an hash function name, quser should be the external
identification of user and the function hashlogin is called to convert
such id to a WIMS login. If the user exists in class, it returns a
session number as above. If the user does not exists, the WIMS login is
returned in the error message.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.
* hashlogin  - (str) hash function to use for an external authentification


## buildexos
**`buildexos(self, qclass, rclass, verbose=False, code=None, **kwargs)`**

Compile every exercises of the specified class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.


## checkclass
**`checkclass(self, qclass, rclass, verbose=False, code=None, **kwargs)`**

Check whether the class accepts connection.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.

## checkexam
**`checkexam(self, qclass, rclass, qexam, verbose=False, code=None, **kwargs)`**

Check whether the exam exists.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qexam  - (str) exam identifier on the receiving server.


## checkident
**`checkident(self, verbose=False, code=None, **kwargs)`**

Check whether the connection is accepted.


## checksheet
**`checksheet(self, qclass, rclass, qsheet, verbose=False, code=None, **kwargs)`**

Check whether the sheet exists.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (str) identifier of the sheet on the receiving server.


## checkuser
`**checkuser(self, qclass, rclass, quser, verbose=False, code=None, **kwargs)**`

Check whether the user exists.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.


## cleanclass
**`cleanclass(self, qclass, rclass, verbose=False, code=None, **kwargs)`**

Delete users (but supervisor) and all work done by students on the specified class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.


## copyclass
**`copyclass(self, qclass, rclass, verbose=False, code=None, **kwargs)`**

Copy a class. Do not copy users or work done by students.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.

## delclass
**`delclass(self, qclass, rclass, verbose=False, code=None, **kwargs)`**

Delete a class.

***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.


## delexam
**`delexam(self, qclass, rclass, qexam, verbose=False, code=None, **kwargs)`**

Delete an exam.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qexam   - (str) exam identifier on the receiving server.


## delexo
**`delexo(self, qclass, rclass, qexo, verbose=False, code=None, **kwargs)`**

Delete an exo.

***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qexo   - (str) exo identifier on the receiving server.


## delsheet
**`delsheet(self, qclass, rclass, qsheet, verbose=False, code=None, **kwargs)`**

Delete a sheet
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (int) identifier of the sheet on the receiving server.
* options - (list) names of fields queried.

## deluser
**`deluser(self, qclass, rclass, quser, verbose=False, code=None, **kwargs)`**

Delete an user.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.


## getclass
**`getclass(self, qclass, rclass, options=None, verbose=False, code=None, **kwargs)`**

Get the properties of a class.
 
Optionally, the parameter 'options' may contain the names of fields
queried. In this case, only the queried properties are returned.
 
Existing properties are: password, creator, secure, external_auth, mixed_external_auth,
cas_auth, php_auth, authidp, supervisor, description, institution, lang, email, expiration,
limit, topscores, superclass, type, level, parent, typename, bgcolor, bgimg, scorecolor,
css, logo, logoside, refcolor, ref_menucolor, ref_button_color, ref_button_bgcolor,
ref_button_help_color, ref_button_help_bgcolor, theme, theme_icon, connections, creation,
userlist, usercount, examcount, sheetcount
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* options - (list) names of fields queried.


## getclassesuser
**`getclassesuser(self, rclass, quser, verbose=False, code=None, **kwargs)`**

List all the classes having connection with rclass where quser exists.
 
Optionally, the parameter 'options' may contain the names of fields
queried for each class. In this case, only the queried properties are returned.
 
Existing properties are: password, creator, secure, external_auth, mixed_external_auth,
cas_auth, php_auth, authidp, supervisor, description, institution, lang, email, expiration,
limit, topscores, superclass, type, level, parent, typename, bgcolor, bgimg, scorecolor,
css, logo, logoside, refcolor, ref_menucolor, ref_button_color, ref_button_bgcolor,
ref_button_help_color, ref_button_help_bgcolor, theme, theme_icon, connections, creation,
userlist, usercount, examcount, sheetcount
     
***Parameters:***

* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.
* options - (list) names of fields queried.

## getclassfile
**`getclassfile(self, qclass, rclass, filename, code=None, **kwargs)`**

Download the file <filename> of the specified class.
     
***Parameters:***

* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.


## getclassmodif
**`getclassmodif(self, qclass, rclass, date, verbose=False, code=None, **kwargs)`**

List all the files modified on the specified class since <date>.
     
***Parameters:***

* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.
* date   - (str) date (yyyymmdd)

## getclasstgz
**`getclasstgz(self, qclass, rclass, code=None, **kwargs)`**

Download the class in a compressed (tar-gzip) file.
     
***Parameters:***

* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.

## getcsv
**`getcsv(self, qclass, rclass, options, format='csv', code=None, **kwargs)`**

Get data of the class, under the form of a csv/tsv/xls spreatsheet file.
 
The parameter 'format' may be used to specify the desired output format
(csv or tsv, defaults to csv).
 
The parameter 'options' should contain a list of desired data columns.
The following names can be included in 'option', with their respective meanings:

* login       : user identifiers
* password    : user passwords (uncrypted)
* name        : user names (last name and first name)
* lastname    : user family names
* firstname   : user given names
* email       : user email addresses
* regnum      : user registration numbers
* allscore    : all score fields (averages and details)
* averages    : score averages (average0, average1, average2)
* average0    : global score average (as computed by WIMS)
* average1    : average of scores automatically attributed by WIMS
* average2    : average of teacher-entered scores
* exams       : exam1+exam2+...
* exam1, exam2, ...: scores of each exam
* sheets      : sheet1+sheet2+...
* sheet1, sheet2, ...: scores of each worksheet
* manuals     : manual1+manual2+...
* manual1, manual2, ...: first, second, ... teacher-entered scores.
     
The output content (below the status line in WIMS format) is a csv/tsv
spreadsheet table. The first row of the table contains
the names of the fields. The second row gives short
descriptions of each field. The third row is blank.
The rest is the table content, with one row for each user.
 
***Parameters:***

* qclass  - (int) identifier of the class on the receiving server.
* rclass  - (str) identifier of the class on the sending server.
* options - (list) list of desired data columns.
* format  - (str) output format ('csv', 'tsv' or 'xls', defaults to csv)

## getexam
**`getexam(self, qclass, rclass, qexam, verbose=False, code=None, **kwargs)`**

Get an exam from a class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qexam  - (int) identifier of the exam on the receiving server.

## getexamlog
**`getexamlog(self, qclass, rclass, quser, qexam, verbose=False, code=None, **kwargs)`**

Get the logs of <quser> on <qexam> inside of a class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* quser  - (int) identifier of the user on the receiving server.
* qexam  - (int) identifier of the exam on the receiving server.

## getexamscores
**`getexamscores(self, qclass, rclass, qexam, verbose=False, code=None, **kwargs)`**

Get all scores from exam.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qexam  - (int) identifier of the exam on the receiving server.

getexo(self, qclass, rclass, qsheet, qexo, verbose=False, code=None, **kwargs)
    Get an exercice from a sheet.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (int) identifier of the sheet on the receiving server.
* qexo   - (int) identifier of the exo on the receiving server.

## getexofile
**`getexofile(self, qclass, rclass, qexo, code=None, **kwargs)`**

Download the <qexo> source file of the specified class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qexo   - (int) identifier of the exo on the receiving server.

## getexosheet
**`getexosheet(self, qclass, rclass, qsheet, qexo, verbose=False, code=None, **kwargs)`**

Get informations of <qexo> inside of <qsheet> of the specified class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (int) identifier of the sheet on the receiving server.
* qexo   - (int) identifier of the exo on the receiving server.

## getinfoserver
**`getinfoserver(self, verbose=False, code=None, **kwargs)`**

Get informations about the WIMS server.

## getlog
**`getlog(self, qclass, rclass, quser, verbose=False, code=None, **kwargs)`**

Get the detailed activity registry of an user.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.

## getmodule
**`getmodule(self, module, verbose=False, code=None, **kwargs)`**

Get informations about <module>.
     
***Parameters:***

* module - (str) path of a module (i.e. 'E1/geometry/oefsquare.fr')

## getscore
**`getscore(self, qclass, rclass, quser, qsheet=None, verbose=False, code=None, **kwargs)`**

Get all scores from user.
Can optionnally filter from a sheet.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.
* qsheet - (int) identifier of the sheet on the receiving server.
                 Used to filter the scores.

## getscores
**`getscores(self, qclass, rclass, options, code=None, **kwargs)`**

Call `getcsv()` method with format='xls'.
For more informations, see `WimsAPI.getcsv()` documentation.

## getsession
**`getsession(self, data1='adm/createxo', verbose=False, code=None, **kwargs)`**

Open a WIMS session and return its ID

## getsheet
**`getsheet(self, qclass, rclass, qsheet, options=None, verbose=False, code=None, **kwargs)`**

Get the properties of a sheet (of a class).
 
Optionally, the parameter 'options' may contain the names of fields
queried. In this case, only the queried properties are returned.
 
Existing properties are: exo_cnt, sheet_properties, sheet_status, sheet_expiration,
sheet_title, sheet_description, exolist, title, params, points, weight, description
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (int) identifier of the sheet on the receiving server.
* options - (list) names of fields queried.

## getsheetscores
**`getsheetscores(self, qclass, rclass, qsheet, verbose=False, code=None, **kwargs)`**

Get all scores from sheet.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (int) identifier of the sheet on the receiving server.

## getsheetstats
**`getsheetstats(self, qclass, rclass, qsheet, verbose=False, code=None, **kwargs)`**

Get stats about work of students for every exercise of <qsheet>.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (int) identifier of the sheet on the receiving server.

## gettime
**`gettime(self, verbose=False, code=None, **kwargs)`**

Get the current time of the server.
     
    Can be used for synchronization purposes.

## getuser
**`getuser(self, qclass, rclass, quser, options=None, verbose=False, code=None, **kwargs)`**

Get the properties of an user (of a class).
     
Optionally, the parameter 'options' may contain the names of fields
queried. In this case, only the queried properties are returned.
 
Existing properties are: firstname, lastname, email, comments, regnum, photourl,
participate, password, courses, classes, supervise, supervisable, external_auth,
agreecgu, regprop1,
regprop2, regprop3, regprop4, regprop5
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.
* options - (list) names of fields queried.

## lightpopup
**`lightpopup(self, qclass, rclass, quser, session, exercice, about=True, code=None, **kwargs)`**

Presents an exercise without the top, bottom, and left menu
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.
* session - (str) session identifer returned by authuser().
* exercice - (str) addresse of the exercice found in 'About this module / this exercice'
                   on the page of the exercice eg:
                   'classes/en&exo=Exercise1&qnum=1&qcmlevel=1&scoredelay=700,700 '
* about - (bool) If True (default), show "about" which gives author information about the
                 exercise

## linkexo
**`linkexo(self, qclass, rclass, qsheet, qexo, qexam, verbose=False, code=None, **kwargs)`**

Add exercise <qexo> of the sheet <qsheet> to <qexam>.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (int) identifier of the sheet on the receiving server.
* qexam - (int) identifier of the exam on the receiving server.

## linksheet
**`linksheet(self, qclass, rclass, qsheet, qexam, verbose=False, code=None, **kwargs)`**

Add all exercices from sheet to exam.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (int) identifier of the sheet on the receiving server.
* qexam - (int) identifier of the exam on the receiving server.

## listclasses
**`listclasses(self, rclass, verbose=False, code=None, **kwargs)`**

List all the classes having connection with rclass.
 
Optionally, the parameter 'options' may contain the names of fields
queried for each class. In this case, only the queried properties are returned.
 
Existing properties are: password, creator, secure, external_auth, mixed_external_auth,
cas_auth, php_auth, authidp, supervisor, description, institution, lang, email, expiration,
limit, topscores, superclass, type, level, parent, typename, bgcolor, bgimg, scorecolor,
css, logo, logoside, refcolor, ref_menucolor, ref_button_color, ref_button_bgcolor,
ref_button_help_color, ref_button_help_bgcolor, theme, theme_icon, connections, creation,
userlist, usercount, examcount, sheetcount
     
***Parameters:***

* rclass - (str) identifier of the class on the sending server.
* options - (list) names of fields queried.

## listexams
**`listexams(self, qclass, rclass, verbose=False, code=None, **kwargs)`**

Lists all exams presents in class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.

## listexos
**`listexos(self, qclass, rclass, verbose=False, code=None, **kwargs)`**

Lists all exercices presents in class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.

## listlinks
**`listlinks(self, qclass, rclass, qsheet, qexam, verbose=False, code=None, **kwargs)`**

Get the number of exercise of <qsheet> linked to <qexam>.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (int) identifier of the sheet on the receiving server.
* qexam - (int) identifier of the exam on the receiving server.

## listmodules
**`listmodules(self, level='H4', verbose=False, code=None, **kwargs)`**

Get the number of exercise of <qsheet> linked to <qexam>.
     
***Parameters:***

* level - (str) level of the module (defaults to H4). Valid levels are E1, E2,
                ..., E6, H1, ..., H6, U1, ..., U5, G, R

## listsheets
**`listsheets(self, qclass, rclass, verbose=False, code=None, **kwargs)`**

List all the sheets of a class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.

## modclass
**`modclass(self, qclass, rclass, class_info, verbose=False, code=None, **kwargs)`**

Modify the properties of a class.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* class_info - (dict) Only modified properties need to be present, following keys
*     *  may be present:
    * description - (str) name of the class
    * institution - (str) name of the institution
    * supervisor - (str) full name of the supervisor
    * email - (str) contact email address
    * password - (str) password for user registration
    * lang - (str) class language (en, fr, es, it, etc)
    * expiration - (str) class expiration date (yyyymmdd, defaults to one year later)
    * limit - (str) limit of number of participants (defaults to 30)
    * level - (str) level of the class (defaults to H4) Valid levels: E1,
                    E2, ..., E6, H1, ..., H6, U1, ..., U5, G, R
    * secure - (str) secure hosts
    * bgcolor - (str) page background color
    * refcolor - (str) menu background color
    * css - (str) css file (must be existing css on the WIMS server)

## modexam
**`modexam(self, qclass, rclass, qexam, exam_info, verbose=False, code=None, **kwargs)`**

Modify the property of an exam.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* exam_info - (dict) Only modified properties need to be present, following keys
                     may be present:
    * title - (str) title of the exam
    * description - (str) description of the exam
    * expiration - (str) exam expiration date (yyyymmdd)
    * duration - (int) duration (in minutes)
    * attempts - (int) number of attempts

## modexosheet
**`modexosheet(self, verbose=False, code=None, **kwargs)`**

***Not implemented yet.***

## modsheet
**`modsheet(self, qclass, rclass, qsheet, sheet_info, verbose=False, code=None, **kwargs)`**

Modify the properties of a sheet.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (int) identifier of the sheet on the receiving server.
* sheet_info - (dict) Only modified properties need to be present, following keys
                      may be present:
    * title - (str) name of the sheet (defaults to "sheet n#")
    * description - (str) description of the sheet (defaults to "sheet n#")
    * expiration - (str) expiration date (yyyymmdd) defaults to one year later
    * status - (str) the mode of the sheet. 0 : pending (default), 1 : active, 
                     2 : expired, 3 : expired + hidden
    * weight - (str) weight of the sheet in class score
    * formula - (str) How the score is calculated for this sheet (0 to 6)
    * indicator - (str) what indicator will be used in the score formula (0 to 2)
    * contents - (str) the contents for the multi-line file to be created.
                       The semicolons (;) in this parameter will be
                       interpreted as new lines. Equal characters (=) must
                       be replaced by the character AT (@).
                       There is no check made, so the integrity of the
                       contents is up to you only! (defaults to "")

## moduser
**`moduser(self, qclass, rclass, quser, user_info, verbose=False, code=None, **kwargs)`**

Modify the properties of an user.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.
* user_info - (dict) Only modified properties need to be present, following keys
                     may be present:
    * lastname - (str) last name of the supervisor user
    * firstname - (str) first name of the supervisor user
    * password - (str) user's password, non-crypted.
    * email - (str) email address
    * comments - (str) any comments
    * regnum - (str) registration number
    * photourl - (str) url of user's photo
    * participate - (str) list classes where user participates
    * courses - (str) special for portal
    * classes - (str) special for portal
    * supervise - (str) List classes where teacher are administator
    * supervisable - (str) yes/no ; give right to the user to supervise a class
    * external_auth - (str) login for external_auth
    * agreecgu - (str) if yes, the user will not be asked when he enters
    * * for the first time to agree the cgu
    * regprop[1..5] - (str) custom variables

## movexo
**`movexo(self, qclass, qclass2, rclass, qsheet, copy=False, verbose=False, code=None, **kwargs)`**

Moves exercice from qclass to qclass2.
     
    Condition : Both 2 classes must be linked by.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server, source of the exo.
* qclass2 - (int) identifier of the class on the receiving server, destination of the exo.
* rclass - (str) identifier of the class on the sending server.
* qsheet - (int) identifier of the sheet on the receiving server.
* copy - (bool) If set to True, copy the exo instead of moving it.

## movexos
**`movexos(self, qclass, qclass2, rclass, copy=False, verbose=False, code=None, **kwargs)`**

Moves ALL exercices from qclass to qclass2.
     
    Condition : Both 2 classes must be linked by.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server, source of the exos.
* qclass2 - (int) identifier of the class on the receiving server, destination of the exo.
* rclass - (str) identifier of the class on the sending server.
* copy - (bool) If set to True, copy the exo instead of moving it.

## putcsv
**`putcsv(self, qclass, rclass, csv, file=True, verbose=False, code=None, **kwargs)`**

Put data into the class.
 
csv should respect this format: The first row of the table contains
the names of the fields. The second row gives short
descriptions of each field. The second row is blank.
The rest is the table content, with one row for each user.
The following data columns can be included in the csv, with their respective meanings:

* login       : user identifiers
* password    : user passwords (uncrypted)
* name        : user names (last name and first name)
* lastname    : user family names
* firstname   : user given names
* email       : user email addresses
* regnum      : user registration numbers
* allscore    : all score fields (averages and details)
* averages    : score averages (average0, average1, average2)
* average0    : global score average (as computed by WIMS)
* average1    : average of scores automatically attributed by WIMS
* average2    : average of teacher-entered scores
* exams       : exam1+exam2+...
* exam1, exam2, ...: scores of each exam
* sheets      : sheet1+sheet2+...
* sheet1, sheet2, ...: scores of each worksheet
* manuals     : manual1+manual2+...
* manual1, manual2, ...: first, second, ... teacher-entered scores.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* csv    - (str) path to a csv if 'file' is True (default), content of a csv otherwise.
* file   - (bool) Whether csv must be interpreted as a path to a csv or a .csv string

## putexo
**`putexo(self, qclass, rclass, qsheet, module, options=None, verbose=False, code=None, **kwargs)`**

Add <module>'s exercise to <qsheet> of a specified class.
     
***Parameters:***

* qclass  - (int) identifier of the class on the receiving server.
* rclass  - (str) identifier of the class on the sending server.
* qsheet  - (str) sheet identifier on the receiving server.
* module  - (str) path of a module (i.e. 'E1/geometry/oefsquare.fr').
* options - (dict) A dictionnary of optionnal parameters:
    * params - (str) string of parameters to add to the module.
    * points - (int) number of requested points.
    * weight - (int) weight of the exercise.
    * title  - (str) title of the exercise in the sheet.
    * description  - (str) description of the exercise in the sheet.

## recuser
**`recuser(self, qclass, rclass, quser, verbose=False, code=None, **kwargs)`**

Recover a deleted user.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* quser  - (str) user identifier on the receiving server.

## repairclass
**`repairclass(self, qclass, rclass, verbose=False, code=None, **kwargs)`**

Try to detect and correct eventual problems.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.

## search
**`search(self, verbose=False, code=None, **kwargs)`**

***Not implemented yet.***


## sharerecontent
**`sharerecontent(self, qclass, qclass2, rclass, options=('exo',), verbose=False, code=None, **kwargs)`**

Declares neighbour classes, allowing class "qclass" to share content with class "data1".
Both classes must be linked by.
     
***Parameters:***

* qclass - (int) identifier of the class on the receiving server.
* qclass2 - (int) identifier of the second class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* options - (list) content to share (currently, only the "exo" content type is supported).

## testexo
**`testexo(self, exo_src, verbose=False, code=None, **kwargs)`**

Allow to test the compilation of an exercise without adding it to a class.
     
***Parameters:***

* exo_src - (str) source of the exercice.

## update
**`update(self, verbose=False, code=None, **kwargs)`**

***Not implemented yet.***
