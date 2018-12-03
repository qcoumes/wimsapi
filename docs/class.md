# Class

On *WIMS*, a **Class** is the main structure. Each class contains its own 
[Users](user.md), [Sheets](sheet.md), [Exercises](exercise.md) and 
[Exams](exam.md).


## Instantiation

To get a **Class** instance, you have two possibility. You can either create a new
instance, or get one from the *WIMS* server.

To create a new instance, you'll need an [User](user.md) to use as a supervisor.

```python
from wimsapi import Class, User

user = User("quser", "lastname", "firstname", "password", "mail@mail.com")
c = Class(9999, "rclass", "Title", "Institution", "mail@mail.com", "password", user)
```

**Note:** The quser of the [User](user.md) used to create the supervisor does
not matter, it will be overwritten with "supervisor" as soon as the class is
saved.

**Class** can also take a lot of optionnal argument:

> `Class(qclass, rclass, name, institution, email, password, supervisor, lang="en",  date=None, limit=30, level="H4", secure='all', bgcolor='', refcolor='', css='')`

Where:

* qclass - (int) identifier of the class on the receiving server.
* rclass - (str) identifier of the class on the sending server.
* name - (str) name of the class.
* institution - (str) name of the institution.
* email - (str) contact email address.
* password - (str) password for user registration.
* supervisor - (wimsapi.user.User) An WIMS user instance representing the supervisor.
* lang - (str) class language (en, fr, es, it, etc).
* expiration - (str) class expiration date (yyyymmdd, defaults to one year later).
* limit - (str) limit of number of participants (defaults to 30).
* level - (str) level of the class (defaults to H4) Valid levels: E1,
                E2, ..., E6, H1, ..., H6, U1, ..., U5, G, R
* secure - (str) secure hosts.
* bgcolor - (str) page background color.
* refcolor - (str) menu background color.
* css - (str) css file (must be existing css on the WIMS server)."""


___

To get an instance from the *WIMS* server, you can use the class method :

> `Class.get(url, ident, passwd, qclass, rclass)`

Where :

* `url` is the url to the *WIMS* server's cgi (eg. 
  https://wims.unice.fr/wims/wims.cgi).
* `ident` and `password` are credentials
  as defined in `[WIMS_HOME]/log/classes/.connections/` (see 
  [configuration](index.md#configuration))
* `qclass` is the ID of the class on
  the *WIMS* server (name of the directory corresponding to the class in
  `[WIMS_HOME]/log/classes/[ID]`)
* `rclass` the identifier corresponding to
  the class (again, see [configuration](index.md#configuration)).


## Saving

Any changes made to a **Class** instance can be reflected on the *WIMS* server
with the method `save()` :

```python
from wimsapi import Class
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
c.institution = "Another institution"
c.save()
```

If the **Class** has been instatiated through its constructor, and not with
`Class.get()` method, and has not been saved yet, you will need to provide
the server's url, ident, and passwd (see [configuration](index.md#configuration)) :

```python
c = Class(999999, "myclass", "Title", "Institution", "mail@mail.com", "password",  user)
c.save("https://wims.unice.fr/wims/wims.cgi", "myself", "toto")
c.institution = "Another institution"
c.save()
```


## Reloading an instance

To reflect server-side changes on an instance of **Class**, use `refresh()` :

```python
c = Class(9999, "myclass", "Title", "Institution", "mail@mail.com", "password",  supervisor)
c.save("https://wims.unice.fr/wims/wims.cgi", "myself", "toto")

c2 = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")

c.institution = "Another institution"
c.save()

c2.institution # "Institution"
c2.refresh()
c2.institution # "Another institution"
```



## Deleting
To delete an already saved **Class**, simply use `delete()`:

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
c.delete()
```


## More Data

Once the **Class** has been saved you can acceed the additionnal fields `ident`,
`passwd`, `url` and `infos` :

```python
c = Class(999999, "myclass", "Title", "Institution", "mail@mail.com", "password",  user)
c.save("https://wims.unice.fr/wims/wims.cgi", "myself", "toto")
c.ident # "myself"
c.passwd # "toto"
c.url # "https://wims.unice.fr/wims/wims.cgi"
c.infos
# {
#     'query_class': '999999', 'rclass': 'myclass', 'password': 'password',
#     'creator': '172.17.0.1', 'secure': 'all', 'external_auth': '',
#     'mixed_external_auth': '', 'cas_auth': '', 'php_auth': '',
#     'authidp': '', 'supervisor': 'Firstname Lastname',
#     'description': 'Title', 'institution': 'Institution', 'lang': 'en',
#     'email': 'mail@mail.com', 'expiration': '20191127', 'limit': '30',
#     'topscores': '', 'superclass': '', 'type': '0', 'level': 'H4',
#     'parent': '', 'typename': 'class', 'bgcolor': '', 'bgimg': '',
#     'scorecolor': '#ffffff, #ff0000, #ff0000, #ff0000, #ffa500, #ffa500,
#         #fff500, #d2ff00, #b9ff00, #2fc42f, #259425',
#     'css': '-theme-', 'logo': '', 'logoside': '', 'refcolor': '',
#     'ref_menucolor': '', 'ref_button_color': '', 'ref_button_bgcolor': '',
#     'ref_button_help_color': '', 'ref_button_help_bgcolor': '',
#     'theme': 'standard', 'theme_icon': '', 'sendmailteacher': '', 
#     'connections': '+myself/myclass+  ', 'creation': '20181127',
#     'userlist': [''], 'usercount': '0', 'examcount': '0', 'sheetcount': '0'
# }


```


## Items

**Class** has 4 methods allowing it to interact with its [User](user.md),
[Sheets](sheet.md), [Exercises](exercise.md) and [Exams](exam.md).


### Add an item

You can add an item with the method `additem(item)`, where *item* is an instance of
[User](user.md), [Sheets](sheet.md), [Exercises](exercise.md) or [Exams](exam.md).

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
user = User("quser", "lastname", "firstname", "password", "mail@mail.com")
c.additem(user)
```


### Get an item

You can retrieve an item with the method `getitem(identifier, cls)`, where *cls* is the
python class [User](user.md), [Sheets](sheet.md), [Exercises](exercise.md) or [Exams](exam.md),
and *identifier* it's ID on the WIMS class.

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
user = User("quser", "lastname", "firstname", "password", "mail@mail.com")
c.additem(user)
u = c.getitem("quser", User)
```


### Delete an item

You can delete an item from a *WIMS* class with the method `delitem(item, cls=None)`.
*Item* must be either an instance of [User](user.md), [Sheets](sheet.md),
[Exercises](exercise.md) or [Exams](exam.md) ; or string. If item is a string, cls
must be provided and be the corresponding python class.

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
user = User("quser", "lastname", "firstname", "password", "mail@mail.com")
c.additem(user)

c.delitem(user)
# OR
c.delitem("quser", User)
```


### Check if an item is in the class

You can check if an item is in a *WIMS* class with the method `checkitem(item, cls=None)`.
*Item* must be either an instance of [User](user.md), [Sheets](sheet.md),
[Exercises](exercise.md), [Exams](exam.md), or string. If item is a string, cls
must be provided and be the corresponding python class.

This method returns True if the item is present in the WIMS class, False otherwise.

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
user = User("quser", "lastname", "firstname", "password", "mail@mail.com")
unknown = User("unknown", "lastname", "firstname", "password", "mail@mail.com")
c.additem(user)

c.checkitem(user) # True
c.checkitem(unknown) # False
# OR
c.checkitem("quser", User) # True
c.checkitem("unknown", User) # False
```


You can also use `item in class` operator, where item is an instance of 
[User](user.md), [Sheets](sheet.md), [Exercises](exercise.md) or [Exams](exam.md).

```python
user in c # True
unknown in c # False
```