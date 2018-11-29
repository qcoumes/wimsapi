# Exceptions


## wimsapi.WimsAPIError

The base exception for all **wimsapi** exceptions.


## wimsapi.NotSavedError

Raised trying to use a method needing an object to be saved, without the object being
actually saved (e.g. deleting an unsaved [Class](class.md))


## wimsapi.InvalidItemTypeError

Raised by

* `Class.additem(object, cls)`
* `Class.delitem(object, cls)`
* `Class.getitem(object, cls)`
* `Class.checkitem(object, cls)`

if given `object` or `cls` is not a valid *WIMS* class item type
(See [Class](class.md)).


## wimsapi.AdmRawError

Raised either when sending an invalid request to the *WIMS* server (e.g. getting
a user that does not exists) or when the *WIMS* server encounter an unknown error.

The response from the *WIMS* server is usually in the exception's message.
