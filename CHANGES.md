# Changelog


### 0.4.1

* Listing functions now return an empty list when needed


## 0.4.0

* Added new item : `Sheet`
* Added the possibility to list items and classes through `Class.list()` and
    `class.listitem()`.
* Added `__eq__()` for items and classes.
* Fixed some documentation


### 0.3.9

* Renamed Class member `date` to `expiration` to match the *ADM/RAW* argument.
* `Class.limit` is now an *int* when retrieving the class from a *WIMS* server.
* Now propagate exception if expiration in Class `__init__` is not `yyyymmdd`.

### 0.3.7 & 0.3.8

* `check_exists` is now used properly


### 0.3.6

* Added `check_exists=True` parameter to item's save method.  
    If check_exists is True, the api will check if an item with the same ID
    exists on the WIMS' server. If it exists, save will instead modify this
    item instead of trying to create new one.  
    `wclass.additem()` will now use `check_exists=False`.
* Fix response check in `wclass.save()`


### 0.3.5

* Fix missing `self.lang = lang` in **Class**' `__init__`


### 0.3.4

* Fix `long_description` in setup.py


### 0.3.3

* `qclass` argument is now optionnal in Class constructor,
   allowing WIMS to choose a free `qclass` when saving for
   the fist time. 


### 0.3.2

* Fixed `WimsAPI.putexo()`.
* Updated tests and unskipped some according to latest WIMS version.


### 0.3.1

* Fixed buggy import in setup.py


## 0.3.0

* Adding **Classe** higher level API, allowing to manipulate a WIMS' Class.
* Adding **User** higher level API, allowing to manipulate a WIMS' User.
* Adding documentation.


### 0.2.2

* More tests.


### 0.2.1

* Fixed travis CI.


## 0.2.0

* Add User and Class higher level classes.
* Add some tests fomr WimsApi.
* Add Travis CI.


## 0.1.0

* Initial public release.
