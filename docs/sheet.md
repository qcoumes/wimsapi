# Sheet

The first time a **Sheet** is saved in a [Class](class.md), the corresponding
instance of the class is then link to the **Sheet** through the `.wclass`
attribute. This allow to use some methods such as `delete()` or `save()`
without any argument.  
The instance of [Class](class.md) is also link to a **Sheet** obtained through
`Class.getitem()` or `Sheet.get()`.


## Instantiation

To get a **Sheet** instance, you have two possibility. You can either create a new
instance, or get one from the *WIMS* server.

To create a new instance :

```python
from wimsapi import Sheet

sheet = Sheet("Title", "Description")
```

**Sheet** can also take a lot of optionnal argument:

> `Sheet(title, description, expiration=None, sheetmode=0, weight=1, formula=2, indicator=1, contents="")`

Where:

* title - (str) name of the sheet (defaults to "sheet n#")
* description - (str) description of the sheet (defaults to "sheet n#")
* expiration - (str) expiration date (yyyymmdd) defaults to one year later
* sheetmode - (str) the mode of the sheet:
    * 0 : pending (default)
    * 1 : active
    * 2 : expired
    * 3 : expired + hidden
* weight - (int) weight of the sheet in the class score (default to 1), use 0 if you want this sheet's score to be ignored.
* formula - (str) How the score is calculated for this sheet (0 to 6, default to 2)
    * 0 : Very lenient: maximum between percentage and quality.
    * 1 : Quality is not taken into account. You get maximum of grade once all the required work is done.
    * 2 : Quality has only slight effect over the grade.
    * 3 : More effect of quality.
    * 4 : To have a grade of 10, you must gather all required points (100%) without making any error (quality=10).
    * 5 : Unfinished work is over-punished.
    * 6 : Any mistake is over-punished.
* indicator - (str) what indicator will be used in the score formula (0 to 2, default to 1)
* contents - (str) the contents for the multi-line file to be created. The semicolons (;) in this
    parameter will be interpreted as new lines. Equal characters (=) must be replaced by the character AT (@).
    There is no check made, so the integrity of the contents is up to you only! (defaults to "")"""


___

To get an instance from the *WIMS* server, you can use either of the following
class method :

> `Sheet.get(wclass, qsheet)`

Where :

* `wclass` is an instance of [Class](class.md) which the **Sheet** belong to.
* `Sheet` is the identifier corresponding to the sheet.

or

> `c.getitem(qsheet, Sheet)`

Where :

* `c` is an instance of [Class](class.md) which the **Sheet** belong to.
* `qsheet` is the identifier corresponding to the sheet.
* `Sheet` the Sheet class.



## Saving

Any changes made to a **Sheet** instance can be reflected on the *WIMS* server
with the method `save()` :

```python
from wimsapi import Class, Sheet
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
s = Sheet.get(c, "qsheet")
s.firstname = "Newname"
s.save()
```

If the **Sheet** has been instantiated through its constructor, and not with
one of the `get` method, and has not been saved yet, you will need to provide
a [Class](class.md) which had already been saved on the server.

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
s = Sheet("qsheet", "lastname", "firstname", "password", "mail@mail.com")
s.save(c)
```

To add an **Sheet** to a **Class**, you can also use `c.additem(sheet)`.

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
s = Sheet("qsheet", "lastname", "firstname", "password", "mail@mail.com")
c.additem(s)
```

In fact, `c.additem(sheet)` will call `sheet.save(c)`, therefore if a same sheet is added
to multiple classes through `s.save(c)` or `c.additem(s)`, future call to `s.save()`
will only save changed on the last Class the Sheet has been saved to.

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
c2 = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 8888, "myclass")
s = Sheet("qsheet", "lastname", "firstname", "password", "mail@mail.com")

c.additem(s)
s.save(c2)
s.firstname = "Newname"
s.save()  # Only save changes on c2
```


## Reloading an instance

To reflect server-side changes on an instance of **Sheet**, use `refresh()` :

```python
s.title = "Old"
c.save(s)

s2 = c.getitem(s.qsheet, Sheet)

s2.title = "New"
s2.save()

s.institution # "Old"
s.refresh()
s.institution # "New"
```


## Deleting
To delete an already saved **Sheet** `s` from a [Class](class.md) `c`, you have a lot
possibility:

* `s.delete()`
* `Sheet.delete(c, s)`
* `Sheet.delete(c, "qsheet")` where `"qsheet" == s.qsheet`
* `c.delitem(s)`
* `c.delitem("qsheet", Sheet)` where `"qsheet" == s.qsheet`


## Check if a sheet exists in a WIMS class

To check whether **Sheet** `u` is in a [Class](class.md) `c`, you have once again
a lot of possibility:

* `Sheet.check(c, s)`
* `Sheet.check(c, "qsheet")` where `"qsheet" == s.qsheet`
* `c.checkitem(s)`
* `c.checkitem("qsheet", Sheet)` where `"qsheet" == s.qsheet`
* `s in c`

All of these methods return `True` if the sheet exists in the class,
`False` otherwise.

## More Data

Once the **Sheet** has been saved you can acceed the additionnal fields `infos`
and `wclass` which is the instance of [Class](class.md) this sheet is saved on:

```python
c = Class.get("https://wims.unice.fr/wims/wims.cgi", "myself", "toto", 9999, "myclass")
s = Sheet("Title", "Description")
c.additem(s)

s.wclass == c # True

c.infos
```

