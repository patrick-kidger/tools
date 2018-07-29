# Tools

Helpful abstract tools (functions, classes, ... ) for coding in Python. Just run `import tools` to get access to them all. Particular highlights:

* `Object` (and its siblings `SortedObject`, `OrderedObject`, `PropObject`), which are dictionaries which can behave a bit like classes, by allowing for `.` attribute look up in place of `[]` notation. (Think of them as a mutable `namedtuple`.)
* `Container`, which allows classes to behave a bit like dictionaries.
* `re_sub_recursive` for recursively regex'ing a string.
* `deepgetattr` and `deepsetattr` which allow for getting and setting attributes of (subsubsub-...)subattributes.
* `classproperty`, which marks a method as being essentially both a classmethod and a property.

Plus a few more esoteric things:
* `SubclassTrackerMixin`, which allows for keeping track of and subsequently locating particular subclasses of a given class.
* `DynamicSubclassingMixin` which allows for dynamically changing the class of an instance on the fly.
* `WithAdder`, which is a mixin that allows for `+`-ing contexts together.
* `combomethod`, which marks a method as being both a classmethod and an instance method.
* `AddBase`, whose `__add__` method always returns whatever the other thing added to it was.

And a few boring-but-useful things:
* `rangeinf`, which is a `range` that allows for `inf` to be passed as the second argument.
* `set_context_variable`, which allows for easily temporarily setting variables to particular values in contexts.
* `nonneg_list`, which is a list that doesn't allow negative indexing.
* `deldict`, which is a dictionary that doesn't mind bad `del` attempts.
* Some basic geometry collisions.

...and other stuff besides!
