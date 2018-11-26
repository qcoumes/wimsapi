# Class

On *WIMS*, a **Class** is the main structure. Each class contains its own 
[Users](user.md), [Sheets](sheet.md), [Exercises](exercise.md) and 
[Exams](exam.md).


## Instantiation

To get a class instance, you have two possibility. You can either create a new
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

Trying to refresh an unsaved **Class** will result in a `wimsapi.NotSavedError`.



## Deleting
To delete an already saved **Class**, simply use `delete()`:

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
c.delete()
```

Trying to delete an unsaved **Class** will result in a `wimsapi.NotSavedError`.


## More Data

Once the **Class** has been saved you can acceed the additionnal fields `ident`,
`passwd`, `url` and `infos` :

```python
c = Class(999999, "myclass", "Title", "Institution", "mail@mail.com", "password",  user)
c.save("https://wims.unice.fr/wims/wims.cgi", "myself", "toto")
c.ident # "myself"
c.passwd # "toto"
c.url # "https://wims.unice.fr/wims/wims.cgi"
c.infos # TODO
```

Trying to acceed to one of these field before saving the **Class** will result
in a `wimsapi.NotSavedError`.



## Users

It's possible to both get and add an [User](user.md) from a **Class** instance,
respectively with the method `get_user()` and `add_user()` :

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
user = c.get_user("quser")

user2 = User("quser2", "lastname", "firstname", "password", "mail@mail.com")
c.add_user(user2)
```

You can neither get nor add user from an unsaved **Class**, any attempt will 
result in a `wimsapi.NotSavedError`.
