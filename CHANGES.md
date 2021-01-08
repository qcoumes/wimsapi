# Changelog

#### 0.5.10

* WIMS accept request saving user with invalid `quser`, removing or changing
  invalid character. But `wimsapi` was taking this change into account, the `quser`
  attribute of the user was thus invalid, causing problem when further communicating with
  the WIMS server.  
  To solve this problem `User.save()` now has a `adapt=True` keyword argument. When `True`,
  the `quser` attribute will be modified to match the one used by WIMS. If `False`, the
  user created on the WIMS server with the modifier `quser` will be deleted and the new
  exception `InvalidIdentifier` will be raised.


#### 0.5.9

* Keyword argument that will be passed to every call of `request.post()` can now
be given to `WimsApi` constructor.
* Every method of `Class` creating a `WimsAPI` can also receive such argument
(`check()`, `save()`, `get()`, `list()`)
* Now use `sdist` instead of `bdist` to create new distribution.

#### 0.5.8

* Now use Github action for testing and publishing

#### 0.5.7

* Added `__str__` method to InvalidResponseError.

#### 0.5.6

* Added `response` field to InvalidResponseError.


#### 0.5.5

* Added InvalidResponseError exception in api.py when WIMS send a badly formatted response.


#### O.5.4

* Append `/` at the end of the WIMS server's url if it is not present when using
`WimsAPI`.

* Added adm/raw API to the documentation.


#### 0.5.3

* Default timeout for low level API is now 10 seconds (instead of 120).


#### 0.5.2

* Parameters of `api.py` requests are now encoding in `ISO-8859-1`, mathching WIMS'
  default encoding
  
* Adding `__repr__` and `__str__` method to `Class` and `Item` subtypes.

* Getting Exams from the WIMS server now retrieve the correct status.


#### 0.5.1

* Fix sheet's score computation


### 0.5.0

* Added classes `Exam` and `ExamScore`, `ExerciseScore` and `SheetScore`
to store scores

* `Sheet` / `Exam`:
    * Title and description are now optionnal in constructor.
    * Added method `scores(user=None)` to retrieve the score of one or every user.

* Added class method `check()` to `Class` to check wheter a class exists or not.

* Better `__eq__` and `__hash__` for every class.


#### 0.4.1

* Listing functions now return an empty list when needed


### 0.4.0

* Added new item : `Sheet`
* Added the possibility to list items and classes through `Class.list()` and
    `class.listitem()`.
* Added `__eq__()` for items and classes.
* Fixed some documentation


#### 0.3.9

* Renamed Class member `date` to `expiration` to match the *ADM/RAW* argument.
* `Class.limit` is now an *int* when retrieving the class from a *WIMS* server.
* Now propagate exception if expiration in Class `__init__` is not `yyyymmdd`.

#### 0.3.7 & 0.3.8

* `check_exists` is now used properly


#### 0.3.6

* Added `check_exists=True` parameter to item's save method.  
    If check_exists is True, the api will check if an item with the same ID
    exists on the WIMS' server. If it exists, save will instead modify this
    item instead of trying to create new one.  
    `wclass.additem()` will now use `check_exists=False`.
* Fix response check in `wclass.save()`


#### 0.3.5

* Fix missing `self.lang = lang` in **Class**' `__init__`


#### 0.3.4

* Fix `long_description` in setup.py


#### 0.3.3

* `qclass` argument is now optionnal in Class constructor,
   allowing WIMS to choose a free `qclass` when saving for
   the fist time. 


#### 0.3.2

* Fixed `WimsAPI.putexo()`.
* Updated tests and unskipped some according to latest WIMS version.


#### 0.3.1

* Fixed buggy import in setup.py


### 0.3.0

* Adding **Classe** higher level API, allowing to manipulate a WIMS' Class.
* Adding **User** higher level API, allowing to manipulate a WIMS' User.
* Adding documentation.


#### 0.2.2

* More tests.


#### 0.2.1

* Fixed travis CI.


### 0.2.0

* Add User and Class higher level classes.
* Add some tests fomr WimsApi.
* Add Travis CI.


### 0.1.0

* Initial public release.
