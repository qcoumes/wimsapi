[![Build Status](https://travis-ci.org/qcoumes/wimsapi.svg?branch=master)](https://travis-ci.org/qcoumes/wimsapi)
[![PyPI Version](https://badge.fury.io/py/wimsapi.svg)](https://badge.fury.io/py/wimsapi)
[![Coverage Status](https://coveralls.io/repos/github/qcoumes/wimsapi/badge.svg?branch=master)](https://coveralls.io/github/qcoumes/wimsapi?branch=master)
[![Python 3.4+](https://img.shields.io/badge/python-3.5+-brightgreen.svg)](#)
[![License MIT](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/qcoumes/wimsapi/blob/master/LICENSE)


# WimsAPI
A Python 3 implementation of WIMS adm/raw module.

The connectable server must be declared in a file
within the directory `WIMS_HOME/log/classes/.connections/`.

**/!\ Warning: output must be set `ident_type=json` and agent set to `ident_agent=python-requests`
in `WIMS_HOME/log/classes/.connections/IDENT` for
this API to work properly.**



## Install
From source code:


git clone https://github.com/qcoumes/wimsapi.git
cd wimsapi
python setup.py install

With pip:

`pip install django-http-method`



## Low-level API

Many low-level method allow to directly send a request to a WIMS server.
The currently avalaible requests are:
* `addclass()` - Add a class on the receiving server.
* `addexam()` - Add an exam to the specified class.
* `addexo()` - Add an exercice to the specified class.
* `addsheet()` - Add a sheet to the specified cla
* `adduser()` - Add an user to the specified class.
* `authuser()` - Get an authentification token for an user.
* `buildexos()` - Compile every exercises of the specified class.
* `checkclass()` - Check whether the class accepts connection.
* `checkexam()` - Check whether the exam exists.
* `checkident()` - Check whether the connection is accepted.
* `checksheet()` - Check whether the sheet exists.
* `checkuser()` - Check whether the user exists.
* `cleanclass()` - Delete users (but supervisor) and all work done by students on the specified
                   class.
* `copyclass()` - Copy a class. Do not copy users or work done by students.
* `delclass()` - Delete a class.
* `delexam()` - Delete an exam.
* `delexo()` - Delete an exo.
* `delsheet()` - Delete a sheet.
* `deluser()` - Delete an user.
* `getclass()` - Get the properties of a class.
* `getclassesuser()` - List all the classes having connection with rclass where quser exists.
* `getclassfile()` - Download the file <filename> of the specified class.
* `getclassmodif()` - List all the files modified on the specified class since <date>.
* `getclasstgz()` - Download the class in a compressed (tar-gzip) file.
* `getcsv()` - Get data of the class, under the form of a csv/tsv/xls spreatsheet file.
* `getexam()` - Get an exam from a class.
* `getexamlog()` - Get the logs of <quser> on <qexam> inside of a class.
* `getexamscores()` - Get all scores from exam.
* `getexo()` - Get an exercice from a sheet.
* `getexofile()` - Download the <qexo> source file of the specified class.
* `getexosheet()` - Get informations of <qexo> inside of <qsheet> of the specified class.
* `getinfoserver()` - Get informations about the WIMS server.
* `getlog()` - Get the detailed activity registry of an user.
* `getmodule()` - Get informations about <module>.
* `getscore()` - Get all scores from user.
* `getscores()` - Call getcsv() method with format='xls'.
* `getsession()` - Open a WIMS session and return its ID.
* `getsheet()` - Get the properties of a sheet (of a class).
* `getsheetscores()` - Get all scores from sheet.
* `getsheetstats()` - Get stats about work of students for every exercise of <qsheet>.
* `gettime()` - Get the current time of the server.
* `getuser()` - Get the properties of an user of <qclass>.
* `lightpopup()` - Presents an exercise without the top, bottom, and left menu
* `linkexo()` - Add exercise <qexo> of the sheet <qsheet> to <qexam>.
* `linksheet()` - Add all exercices from sheet to exam.
* `listclasses()` - List all the classes having connection with rclass.
* `listexams()` - Lists all exams presents in class.
* `listexos()` - Lists all exercices presents in class.
* `listlinks()` - Get the number of exercise of <qsheet> linked to <qexam>.
* `listmodules()` - Get the number of exercise of <qsheet> linked to <qexam>.
* `listsheets()` - List all the sheets of a class.
* `modclass()` - Modify the properties of a class.
* `modexam()` - Modify the property of an exam.
* ~~modexosheet()~~ - Not implemented yet
* `modsheet()` - Modify the properties of a sheet.
* `moduser()` - Modify the properties of an user.
* `movexo()` - Moves exercice from qclass to qclass2.
* `movexos()` - Moves ALL exercices from qclass to qclass2.
* `putcsv()` - Put data into the class.
* `putexo()` - Add <module>'s exercise to <qsheet> of a specified class.
* `recuser()` - Recover a deleted user.
* `repairclass()` - Try to detect and correct eventual problems.
* ~~search()~~ - Not implemented yet
* `sharecontent()` - Declares neighbour classes, allowing class "qclass" to share content with
                     class "data1"
* `testexo()` - Allow to test the compilation of an exercise without adding it to a class.
* ~~update()~~ - Not implemented yet

Each of these method return a dictionnary containing the response of the WIMS server.

For more information, consult the docstring of the corresponding method in `wimsapi/api.py`.


To use any of these method, you must first declare an object `WimsAPI(url, ident, password)`
where:
* `url` is the url to the wims server CGI. e.g. https://wims.unice.fr/wims/wims.cgi
* `ident` is the sender identifier (a word, according to the definition
          in WIMS_HOME/log/classes/.connections/)
* `password` is the sender password (as defined in WIMS_HOME/log/classes/.connections/)


***Example:***
```python3
>>> from wimsapi import WimsAPI
>>>
>>> api = WimsAPI('https://wims.unice.fr/wims/wims.cgi', 'ident', 'toto')
>>> status, response = api.checkident()
>>> if not status: # Connection failed
        print("Can't establish a connection with the WIMS server: ", response['message'])
>>>
>>> api.getclass(9001, "myclass")
True, {'status': 'OK', 'code': 'I38EDGPL4W', 'job': 'getclass', 'query_class': '9001', 'rclass': 'myclass', 'password': '', 'creator': '', 'secure': 'all', 'external_auth': '', 'mixed_external_auth': '', 'cas_auth': '', 'php_auth': '', 'authidp': '', 'supervisor': 'Sophie, Lemaire; Bernadette, Perrin-Riou', 'description': 'Aide au d veloppement de ressources.', 'institution': 'Classe ouverte pour enseignants', 'lang': 'fr', 'email': 'sophie.lemaire@math.u-psud.fr', 'expiration': '21000101', 'limit': '200', 'topscores': '', 'superclass': '', 'type': '', 'level': 'R', 'parent': '', 'typename': 'class', 'bgcolor': '', 'bgimg': '', 'scorecolor': '', 'css': '-theme-', 'logo': 'gifs/logo/wimsedu.png', 'logoside': 'left', 'refcolor': '', 'ref_menucolor': '', 'ref_button_color': '', 'ref_button_bgcolor': '', 'ref_button_help_color': '', 'ref_button_help_bgcolor': '', 'theme': '', 'theme_icon': '', 'sendmailteacher': '', '': '', 'connections': '+myself/myclass+', 'creation': '20070929', 'userlist': ['anonymous', 'user'], 'usercount': '2', 'examcount': '0', 'sheetcount': '11'}
>>>
>>> api.getclass(170666, "myclass")
False, {'status': 'ERROR', 'code': '6SSLZCEGN6', 'message': 'class 170666 not existing'}
```
