# Protocol for WIMS direct connection with other web servers

WIMS direct communication with another web server is two-directional.
It can receive http/https requests from the other server, and/or send http/https requests to the other.
The connectable server must be declared in a file
within the directory `WIMS_HOME/log/classes/.connections/`.

Requests sent to WIMS should obey the format described below. Results of such requests can be formatted according to the need of the connecting software.

Outgoing requests sent by WIMS can be formatted according to the
specification of the receiving software,
while the result of the request should be formatted according to the need of WIMS, as described below.

_________________________________________________________________
## Request format

A request from a connecting server is an http/https request sent to the main cgi program of the WIMS server, followed by parameter definitions as in a usual http protocol.

All requests must contain the following common parameters:

---
| Name   | Value                      |
|--------|----------------------------|
| module | adm/raw |
| ident  | sender identifier (a word, according to the definition in `WIMS_HOME/log/classes/.connections/`) |
| passwd | sender password (as defined in `WIMS_HOME/log/classes/.connections/`) |
| code   | a random word. This word will be sent back to the sender, in order to allow it to check whether the result is from the good request. |
| job    | type of request, see below. |



 And the following parameters may be added according to the type
of the request.

| Name     | Value                      |
|----------|----------------------------|
| qclass   | identifier of the class on the receiving server. It should be an integer. |
| qprogram |  	|
| quser    | user identifier in the receiving server (when the request concerns a particular user). 	|
| qsheet   | sheet identifier in the receiving server (when the request concerns a particular sheet). 	|
| rclass   | identifier of the class on the sending server. |
| format   | Format of the data. |
| option   | Different meaning according to request. |
| data1    | Different meaning according to request. |


For example, the following request checks whether the class `12345` exists on
the WIMS server `wims.unice.fr`, sent by a connecting server called `friend1` (by
wims.unice.fr), with password `abcde`.

`https://wims.unice.fr/wims/wims.cgi?module=adm/raw&amp;ident=friend1&amp;passwd=abcde&amp;code=afdqreaf1r783&amp;job=checkclass&amp;qclass=12345&amp;rclass=myclass`

Note that for this check to return OK, the class `12345` on wims.unice.fr must
have declared `friend1/myclass` as connectable.
This can be done on an existing class by adding `friend1/myclass` to the `class_connections` parameter in the class `12345` .def file.

_______________________________________________________________________________

## Query output

The query output (that is, the result of the http query) is always of
text/plain type (even if sometimes the output is a binary file).

**WIMS OUTPUT TYPE** : (old fashioned way, non-recommended)
    The first line of the output content is a status line, which is either a
    word OK followed by the random code contained in the request, or the
    word ERROR. If the first line is not as such, then there is a
    serious error in the request or a bug in the server software.
    In case the status is OK, the remaining of the output content is the
    content of the data. Otherwise the second line contains the nature of
    the error.

**JSON OUTPUT TYPE** : (recommended)
    output values are returned json formatted. (see [http://json.org]() for more
    details)
_______________________________________________________________________________

## Types of the requests.

A request to WIMS can have the following types (defined by the parameter 'job')

### job=help
    Show this text.

### job=checkident
    Check whether the connection is accepted.

### job=checkclass
    Check whether the class accepts connection.

### job=checkuser
    Check whether the user exists.

### job=checksheet
    Check whether the sheet exists.

### job=addclass
    Add a class on the receiving server.

For this request, `data1` should be a multi-line text defining the
properties of the new class. Each line contains a definition in the format
`name=value`. (This text must be reformatted for http query string)
The following names may be present in the definitions:

* **mandatory:**
	* description     = name of the class
	* institution     = name of the institution
	* supervisor      = full name of the supervisor
	* email           = contact email address
	* password        = password for user registration
	* lang            = class language (en, fr, es, it, etc)
* **optional:**
	* expiration      = class expiration date (yyyymmdd)
							(optional, defaults to one year later)
	* limit           = limit of number of participants
	                    (optional, defaults to 30)
	* level           = level of the class (optional, defaults to H4)
	                    Valid levels: E1, E2, ..., E6, H1, ..., H6,
			                           U1, ..., U5, G, R
	* secure          = secure hosts
	* bgcolor         = page background color
	* refcolor        = menu background color
	* css             = css file (must be existing css on the WIMS server)

`data2` should be a multi-line text defining the supervisor account, in the
same format as for data1.
The following names may be present in the definitions:

* **mandatory:**
	* lastname        = last name of the supervisor user
	* firstname       = first name of the supervisor user
	* password        = supervisor user's password, non-crypted.
* **optional**
	* email           = supervisor email address
	* comments        = any comments
	* regnum          = registration number
	* photourl        = url of a user picture
	* participate     = list classes (if in a class group) where user participates
	* courses         =
	* classes         =
	* supervise       =
	* supervisable    =
	* external_auth   =
	* agreecgu        = Boolean indicating if user accepted CGU
	* regprop[1..5]   = custom properties


### job=adduser
    Add a user to the specified class.

`data1` should be a multi-line text defining the user account.
The following names may be present in the definitions:

* **mandatory:**
	* lastname        = user's lastname
	* firstname       = user's firstname
	* password        = user's password, non-crypted.
* **optional**
	* email           = email address
	* comments        = any comments
	* regnum          = registration number
	* photourl        = url of user’s photo
	* participate     = list classes where user participates
                          (only for group and portal)
	* courses         = special for portal
	* classes         = special for portal
	* supervise       = List classes where teacher are administator
                          (only for group and portal)
	* supervisable    = `yes/no` ; give right to the user to supervise a class
                          (only for group and portal)
	* external_auth   = login for external_auth (by cas or shiboleth for example).
                          Not useful for Moodle
	* agreecgu        = if yes, the user will not be asked when he enters
                          for the first time to agree the cgu
	* regprop[1..5]   = custom variables, upon to you
                          (i.e : you can set here an external group for example)


### job=modclass
    Modify the properties of a class.

`data1` should be a multi-line text containing the properties to be redefined.
Only modified properties need to be present in data1.


### job=moduser
    Modify the properties of a user. As modclass.

### job=delclass
    Delete a class.

### job=deluser
    Delete a user.

### job=recuser
    Recover a deleted user.

### job=getclass
    Get the properties of a class.

Optionally, the query parameter 'option' may contain the names of fields
queried. In this case, only the queried properties are returned.

**Note**: definitions for portals have beed added to output variables but are not yet in addclass:

    typename            =
    programs            =
    courses             =
    classes             =
    levels              =
    icourses            =
    subclasses          =


### job=getsheet
    Get the properties of a sheet (of a class).

Optionally, the query parameter 'option' may contain
the names of fields queried. In this case, only the
queried properties are returned.

OUTPUT variables:

    queryclass          : the requested class
    querysheet          : the requested sheet
    sheet_properties    : list of properties of the requested sheet
                          (sheet status,expiration date,title,description)
    exocnt              : number of exercices included
    exotitlelist        : list of the exercices included (module:params)


### job=listsheets
    List all the sheets of a class.

OUTPUT variables:

    queryclass       : the requested class
    nbsheet          : number of sheets in this class
    sheettitlelist   : list of the sheets with the format "sheet_id:title"


### job=listclasses
    List all the classes with connection between the `rclass` and `ident/rclass`.

Optionally, the query parameter 'option' contains the name of fields related
to classes asked:
    e.g. : option=description,supervisor


### job=getclassesuser
    List all the classes with connection between the rclass and `ident/rclass` where the user exists.

Optionally, the query parameter 'option' may contain the names of fields
queried. In this case, only the queried properties of the classes are
returned.


### job=getuser
    Get the properties of a user (of a class).

Optionally, the query parameter 'option' may contain the names of fields
to be queried. In this case, only the queried properties are returned.
The output format is as for 'getclass'.


### job=getcsv
    Get data of the class, under the form of a csv/tsv spreatsheet file.

The query parameter 'format' may be used to specify the desired output format
(csv or tsv, defaults to csv).
The query parameter 'option' should contain a list of desired data columns.
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


### job=lightpopup
    Presents an exercise without the top, bottom, and left menu

   The syntax is `job=lightpopup&amp;emod=MODULE` where `MODULE` is an exercise module with its parameters.

   option:

   * about       : show "about" which gives author information about the exercise (default)
   * noabout     : the "about" will not appear.

   SAMPLES REQUESTS:

   * H3/analysis/oeflinf.fr intro in lightpopup mode:
     * [http://127.0.0.1/wims/wims.cgi?module=adm/raw&amp;job=lightpopup&amp;emod=H3%2Fanalysis%2Foeflinf.fr]()

   * "antecedant" exercice from H3/analysis/oeflinf.fr module in lightpopup mode:
     * [http://127.0.0.1/wims/wims.cgi?module=adm/raw&amp;job=lightpopup&amp;emod=H3%2Fanalysis%2Foeflinf.fr&amp;parm=cmd=new;exo=antecedant;qnum=1;qcmlevel=3&amp;option=noabout]()


### job=putcsv
    Put data into the class.

The data to put is sent as the value of the query parameter `data1`, in the
same format as for the query `getcsv` above. And with the following
particularities:
    Field `login` must be present.
    The second row (short descriptions) is not necessary.
    WIMS-attributed scores cannot be uploaded, and will be ignored.
    If all the necessary fields corresponding to user properties (lastname,
    firstname, password, etc.) are present, non-existent users will be
    added to the class. This can be used to install the whole user accounts
    of the class with one request.


### job=getlog
    Get the detailed activity registry of a user.


### job=gettime
    Get the current time of the server

    Can be used for synchronization purposes.


### job=update
    Ask WIMS to update data in a class.

Upon reception of this request, WIMS server will issue queries back to the
remote server, in order to get the up-to-date information and update the
class.
The query parameter 'option' contains the nature of the update request.
It may be one of the following:

	* class       : update class properties (corresponding to modclass)
	* user        : update properties of a user (moduser)
	* scores      : teacher-entered scores (putcsv)


### job=authuser
    Get an authentification for a user.

User's password is not required.
Accepts the query parameter `option=hashlogin`:
    If called with option=hashlogin, `quser` should be the external
    identification of user and the function hashlogin is called to convert
    such id to a WIMS login. If the user exists in class, it returns a
    session number as above. If the user does not exists, the WIMS login is
    returned in the error message.

    OUTPUT :

	* wims_session    : a session number under which the user can connect
                          with no need of further authentification
	* home_url        : a complete URL to connect as authentified.


### job=addsheet
    Add a new sheet to the specified class `qclass`.

`data1` may be defined as a multi-line text defining the sheet defs
The following names may be present in the definitions:

**(optional)**

	* title       = name of the sheet (defaults to "sheet n#")
	* description = description of the sheet (defaults to "sheet n#")
	* expiration  = expiration date (yyyymmdd) defaults to one year later
	* sheetmode   = the mode of the sheet:
		* 0 : pending (default)
		* 1 : active
		* 2 : expired
		* 3 : expired + hidden
	* weight      = weight of the sheet in class score
	* formula     = How the score is calculated for this sheet (0 to 6)
	* indicator   = what indicator will be used in the score formula (0 to 2)
	* contents    = the contents for the multi-line file to be created.
	                  The semicolons (;) in this parameter will be
	                  interpreted as new lines. Equal characters (=) must
	                  be replaced by the character AT (@).
	                  There is no check made, so the integrity of the
	                  contents is up to you only! (defaults to "")

**OUTPUT** :

	* queryclass  : the requested class
	* sheet_id    : id of the new created sheet


### job=addexam
    Add a new exam to the specified class `qclass`.
`data1` may be defined as a multi-line text defining the sheet defs, with the same parameters as in addsheet (see above), plus these additional optional parameters:

* duration   = exam duration
* attempts   = number of authorized attempts
* cut_hours  = Cut hours (format : `yyyymmdd.hh:mm` (separate several hours by spaces).
* opening    = Opening Restrictions (IP ranges / Schedules) opening can set a time restriction for recording notes by adding the words &gt; yyyymmdd.hh:mm (start) and/or &lt; yyyymmdd.hh:mm (end). Dates and times must be in server local time and must be separated by spaces.


### job=addexo
    Add the source file (data1) of an exercise directly to the class, under the name `qexo`


### job=putexo
    Add content (an existing exercise) to the sheet `qsheet` of the `qclass` class
`data1` may be defined as a multi-line text defining the exo defs, according to these parameters:

* **mandatory**
	* module        = the module where comes the erexercice from
* **optional**
	* params        = list of parameters to add to the module
	* points        = number of requested points
	* weight        = Weight of the exercise
	* title         = title of the exercise in the sheet
	* description   = description of the exercise in the sheet


### job=modsheet
    Modify an existing sheet in the specified class.

`data1` may be defined as a multi-line text defining the sheet defs
(cf addsheet)


### job=listexos
    Lists all exercices presents in class `qclass`


### job=movexo
    Moves exercice `qexo` from class `qclass` to class `data1`

Condition : Both 2 classes must be linked by `rclass`

*option*: you can use `copy` to copy file instead of moving it.


### job=movexos
    Moves ALL exercice from class `qclass` to class `data1`

Condition: Both 2 classes must be linked by `rclass`

*option*: you can use `copy` to copy files instead of moving them.


### job=sharecontent
    Declare neighbour classes, allowing class "qclass" to share content with class "data1"

Condition: Both 2 classes must be linked by `rclass`

The `option` parameter can be used to declare which type of content to share
(currently, only the "exo" content type is supported)


### job=linksheet
    Add all exercices from sheet `qsheet` to exam `qexam`


### job=getscore
    Get all scores from user `quser` (optionaly, you can filter with sheet `qsheet`)


### job=getsheetscores
    Get all scores from sheet `qsheet` - JSON OUTPUT only


### job=getexamscores
    Get all scores from exam `qexam`   - JSON OUTPUT only
