[![Build Status](https://travis-ci.org/qcoumes/wimsapi.svg?branch=master)](https://travis-ci.org/qcoumes/wimsapi)
[![PyPI Version](https://badge.fury.io/py/wimsapi.svg)](https://badge.fury.io/py/wimsapi)
[![Coverage Status](https://coveralls.io/repos/github/qcoumes/wimsapi/badge.svg?branch=master)](https://coveralls.io/github/qcoumes/wimsapi?branch=master)
[![Python 3.5+](https://img.shields.io/badge/python-3.5+-brightgreen.svg)](#)
[![Documentation Status](https://readthedocs.org/projects/wimsapi/badge/?version=latest)](https://wimsapi.readthedocs.io/en/latest/?badge=latest)
[![License MIT](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/qcoumes/wimsapi/blob/master/LICENSE)


# Python API for WIMS' adm/raw module

**WimsAPI** is an API written in python3 allowing to communicate with a *WIMS*
server through its *adm/raw* extension.

For more information about *adm/raw*,
[see its documentation](https://wims.auto.u-psud.fr/wims/wims.cgi?module=adm/raw&job=help)

Here the [documentation of wimsapi](https://wimsapi.readthedocs.io/en/latest/).

## Installation

The latest stable version is available on [PyPI](https://pypi.org/project/wimsapi/) :

```bash
pip install wimsapi
```

or from the sources:

```bash
git clone https://github.com/qcoumes/wimsapi
cd wimsapi
python3 setup.py install
```
 

## Configuration

### Global configuration

In order for *WIMS* to accept requests from **WimsAPI**,
a file must be created in `[WIMS_HOME]/log/classes/.connections/`,
the file's name will serve as the identifier name for **WimsAPI**.

Here an exemple of such file:
`[WIMS_HOME]/log/classes/.connections/myself`
```
ident_site=172.17.0.1

ident_desc=This WIMS server

ident_agent=python-requests

# http / https.
ident_protocol=http

# password must be a word composed of alpha-numeric characters.
ident_password=toto

ident_type=json

# The address and identifier/password pair for calling back.
back_url=http://localhost/wims/wims.cgi
back_ident=myself
back_password=toto
```
 
Here a description of the important parameters:

* `ident_site`: a space separated list of IP allowed to send request to this
                *WIMS* server.
* `ident_agent`: ***Must*** be set to `python-requests`.
* `ident_password`: Used alongside the file's name as *identifier* in the request
                    to authenticate yourself on *WIMS*.
* `ident_type`: ***Must*** be set to `json`.

The above example would allow a computer/server of ip `172.17.0.1` to send a request
to the *WIMS* server with identifier *myself* and password *toto*.


### Class Configuration

If you create a class thanks to this API, everything should work perfectly.
However, if you want to use it with an already existing class, some more
configuration must be done.

You must edit the file `[WIMS_HOME]/log/classes/[CLASS_ID]/.def` and add
this line at the end of the file:

```
!set class_connections=+IDENT/RCLASS+
```

Where **IDENT** is the identifier use by the API (name of the corresponding
file in `[WIMS_HOME]/log/classes/.connections/` as defined above) and
**RCLASS** is an identifier sent in the request to authenticate yourself
on the class.

Basically, to authenticate yourself on a class on your *WIMS* server, you
will need :

* `url` : URL to the *WIMS* (`https://wims.unice.fr/wims/wims.cgi` for instance)
* `ident` : Name of the file in `[WIMS_HOME]/log/classes/.connections/`
* `passwd` : Value of `ident_password` in
             `[WIMS_HOME]/log/classes/.connections/[IDENT]`
* `rclass` : Value set after the **/** in `class_connections` in
             `[WIMS_HOME]/log/classes/[CLASS_ID]/.def`



## Example

```python
from wimsapi import Class, User

c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")

c.institution = "Another institution"  # Modify class' institution
c.save()

u = User.get(c, "qcoumes")
u.email = "coumes.quentin@gmail.com"  # Modify user's email
u.save()

new = User("quser", "lastname", "firstname", "password", "mail@mail.com")
c.additem(new)  # Add the new user to the class.
```

For more informations about usage or example : Here the [documentation of wimsapi](https://wimsapi.readthedocs.io/en/latest/).