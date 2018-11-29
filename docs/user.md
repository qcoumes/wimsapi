# User

A weird characteristic of *WIMS* is that an **User** is link to a specific
[Class](class.md), there is no server-wide **User**. Many of the methods should
thus be used against a [Class](class.md).  
The first time an **User** is saved in a [Class](class.md), the corresponding
instance of the class is then link to the **User** through the `.wclass`
attribute. This allow to use some methods such as `delete()` or `save()`
without any argument.  
The instance of [Class](class.md) is also link to an **User** obtained through
`Class.getitem()` or `User.get()`.


## Instantiation

To get an **User** instance, you have two possibility. You can either create a new
instance, or get one from the *WIMS* server.

To create a new instance :

```python
from wimsapi import User

user = User("quser", "lastname", "firstname", "password", "mail@mail.com")
```

**User** can also take a lot of optionnal argument:

> `Class(quser, lastname, firstname, password, email="", comments="", regnum="", photourl="", participate="", courses="", classes="", supervise="", supervisable="no", external_auth="", agreecgu="yes", regprop1="", regprop2="", regprop3="", regprop4="", regprop5="")`

Where:

* quser - (str) user identifier on the receiving server.
* lastname - (str) last name of the user.
* firstname - (str) first name of the user.
* password - (str) user's password, non-crypted.
* email - (str) email address.
* comments - (str) any comments.
* regnum - (str) registration number.
* photourl - (str) url of user's photo.
* participate - (str) list classes where user participates.
* courses - (str) special for portal.
* classes - (str) special for portal.
* supervise - (str) List classes where teacher are administator.
* supervisable - (str) yes/no ; give right to the user to supervise a class (default to 'no').
* external_auth - (str) login for external_auth.
* agreecgu - (str) yes/ no ; if yes, the user will not be asked when he enters
                   for the first time to agree the cgu (default to "yes").
* regprop[1..5] - (str) custom variables.


___

To get an instance from the *WIMS* server, you can use either of the following
class method :

> `User.get(wclass, quser)`

Where :

* `wclass` is an instance of [Class](class.md) which the **User** belong to.
* `quser` is the identifier corresponding to the user.

or

> `c.getitem(quser, User)`

Where :

* `c` is an instance of [Class](class.md) which the **User** belong to.
* `quser` is the identifier corresponding to the user.
* `User` the User class.



## Saving

Any changes made to a **User** instance can be reflected on the *WIMS* server
with the method `save()` :

```python
from wimsapi import Class, User
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
u = User.get(c, "quser")
u.firstname = "Newname"
u.save()
```

If the **Class** has been instatiated through its constructor, and not with
one of the `get` method, and has not been saved yet, you will need to provide
a [Class](class.md) which had already been saved on the server.

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
u = User("quser", "lastname", "firstname", "password", "mail@mail.com")
u.save(c)
```

To add an **User** to a **Class**, you can also use `c.additem(user)`.

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
u = User("quser", "lastname", "firstname", "password", "mail@mail.com")
c.additem(u)
```

In fact, `c.additem(user)` will call `user.save(c)`, therefore if a same user is added
to multiple classes through `u.save(c)` or `c.additem(u)`, future call to `u.save()`
will only save changed on the last Class the User has been saved to.

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
c2 = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 8888, "myclass")
u = User("quser", "lastname", "firstname", "password", "mail@mail.com")

c.additem(u)
u.save(c2)
u.firstname = "Newname"
u.save()  # Only save changes on c2
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
To delete an already saved **User** `u` from a [Class](class.md) `c`, you have a lot
possibility:

* `u.delete()`
* `User.delete(c, u)`
* `User.delete(c, "quser")` where `"quser" == u.quser"`
* `c.delitem(u)`
* `c.delitem("quser", User)` where `"quser" == u.quser"`


## Check if an user exists in a WIMS class

To check whether **User** `u` is in a [Class](class.md) `c`, you have once again
a lot of possibility:

* `User.check(c, u)`
* `User.check(c, "quser")` where `"quser" == u.quser"`
* `c.checkitem(u)`
* `c.checkitem("quser", User)` where `"quser" == u.quser"`

All of these methods return `True` if the user exists in the class,
`False` otherwise.

## More Data

You can acceed to the user fullname with `user.fullname`.

Once the **Class** has been saved you can acceed the additionnal fields `infos`
and `wclass` which is the instance of [Class](class.md) this user is saved on:

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
u = User("quser", "lastname", "firstname", "password", "mail@mail.com")
u.fullname  # Firstname Lastname

c.additem(u)

u.wclass == c # True

c.infos
#{
#   'query_class': '9001', 'queryuser': 'quser', 'firstname': 'firstname',
#   'lastname': 'lastname', 'email': 'mail@mail.com', 'comments': '', 'regnum': '',
#   'photourl': '', 'participate': '', 'courses': '', 'classes': '', 'supervise': '',
#   'supervisable': 'no', 'external_auth': '', 'agreecgu': 'yes', 'regprop1': '',
#   'regprop2': '', 'regprop3': '', 'regprop4': '', 'regprop5': ''
#}



```

