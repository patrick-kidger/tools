"""Objects for storing data."""

import collections
import itertools
import weakref

from . import misc
from . import strings


class Record:
    """Creates a record datatype, roughly equivalent to a mutable tuple with named entries.

    It differs from colletions.namedtuple in that (a) entries are mutable, and (b) it does not need to be defined
    first; we can simply create it from the get-go. (This is also its main difference over something like the PyRecord
    project. It can also be thought of as a counterpart to Object, below, except that Object allows for [] notation
    lookup, and allows for the addition and removal of entries.

    Extra entries cannot be added after creation.

    Example usage:
    >>> class Player:
    ...     def __init__(self, x=1, y=1):
    ...         self.position = Record(x=x, y=y)
    ...
    >>> p = Player()
    >>> p.position.x
    ... 1
    >>> p.position.y = 5
    >>> p.position.y
    ... 5
    Notice how creating a position via PyRecord (or collections.namedtuple, etc.) would all involve an extra line to
    define the class of position before we instantiate it.
    """
    __slots__ = ()
    _record_subclasses = weakref.WeakValueDictionary()

    # Minor hackery incoming.
    # We do it this way so that the following works as you'd expect:
    # >>> r = Record(x=4, y=5)
    # >>> assert isinstance(r, Record)
    # Also so that subclassing Record is also (reasonably) safe.
    def __new__(cls, **kwargs):
        """Should be called with :**kwargs: specifying the names of the entries, and their initial values. e.g.
        >>> r = Record(x=4, y=5)
        """

        if hasattr(cls, '_skip_record'):
            return super(Record, cls).__new__(cls)

        slots = tuple(kwargs.keys())
        try:
            # Reuse existing classes with the correct slots if they exist.
            _Record = cls._record_subclasses[slots]
        except KeyError:
            # Create a class like this so that we don't have to mess around setting __name__ and __qualname__ manually.
            # Set the __slots__ attribute to do what we want in the first place.
            # Set the _skip_record attribute so that we can detect that this is a 'fake' subclass that we shouldn't
            # treat as a genuine subclass of Record.
            _Record = type(cls.__name__,
                           (cls,),
                           {'__slots__': slots,
                            '_skip_record': None})
            # Store the class so we can reuse it later
            cls._record_subclasses[slots] = _Record

        # Actually return an instance of this new class which has the correct __slots__ attribute.
        r = _Record()
        for key, val in kwargs.items():
            setattr(r, key, val)
        return r

    def __init_subclass__(cls, **kwargs):
        super(Record, cls).__init_subclass__(**kwargs)
        # If we're creating a genuine subclass of Record...
        if not hasattr(cls, '_skip_record'):
            # ...then give it somewhere to store its own 'extra subclasses' that it creates in __new__
            cls._record_subclasses = weakref.WeakValueDictionary()

    @classmethod
    def from_dict(cls, dict_):
        """Create an instance from a :dict_: rather than by passing in keyword arguments."""
        return cls(**dict_)

    @classmethod
    def from_args(cls, *args, default_value=None):
        """Creates an instance with names given by :args:, all of which initially take the value :default_value:."""
        dict_ = {key: default_value for key in args}
        return cls.from_dict(dict_)

    def __repr__(self):
        arg_strs = []
        for key in self.__slots__:
            val = getattr(self, key)
            arg_strs.append(f'{key}={val}')
        kwargs = ', '.join(arg_strs)
        return f'{self.__class__.__name__}({kwargs})'


class _ObjectMixin:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            self[key] = self._wrapper(val)
        super(_ObjectMixin, self).__init__()

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)

    @classmethod
    def from_args(cls, *args, default_value=None):
        self = cls()
        for arg in args:
            self[arg] = default_value
        return self
    
    def __getattr__(self, item):
        # This check shouldn't actually be necessary, as magic items should be found through __getattribute__ first.
        if strings.is_magic(item):
            super(_ObjectMixin, self).__getattr__(item)
        else:
            try:
                returnval = self.__getitem__(item)
            except KeyError as e:
                raise AttributeError(e) from e
            else:
                return returnval
        
    def __setattr__(self, item, value):
        if strings.is_magic(item):
            super(_ObjectMixin, self).__setattr__(item, value)
        else:
            self.__setitem__(item, value)
    
    def __delattr__(self, item):
        if strings.is_magic(item):
            super(_ObjectMixin, self).__delattr__(item)
        else:
            try:
                self.__delitem__(item)
            except KeyError as e:
                raise AttributeError(e) from e

    def _wrapper(self, input_):
        return input_


class _SortedMixin:
    def __setitem__(self, key, value, *args, **kwargs):
        shifted_keys = []
        shifted_values = []
        items = iter(list(self.items()))
        for key_, value_ in items:
            if key < key_:
                shifted_keys.append(key_)
                shifted_values.append(value_)
                break
        for key_, value_ in items:
            shifted_keys.append(key_)
            shifted_values.append(value_)
        for key_ in shifted_keys:
            del self[key_]

        super(_SortedMixin, self).__setitem__(key, value, *args, **kwargs)
        for key_, value_ in zip(shifted_keys, shifted_values):
            super(_SortedMixin, self).__setitem__(key_, value_, *args, **kwargs)


class Object(_ObjectMixin, dict):
    """Subclasses dictionary to allow for using . notation to access its stored variables.

    The usual [] notation can still be used, for example when the name of the attribute is not known until runtime.
    The name is a reference to Objects in JavaScript, which behave in this way.

    Basically just a convenience instead of using a plain class or types.SimpleNamespace, besides the fact that it
    supports the [] notation.
    """


class OrderedObject(_ObjectMixin, collections.OrderedDict):
    """An Object which remembers the order its attributes were added in."""


class SortedDict(_SortedMixin, collections.OrderedDict):
    """A dictionary which keeps its key: value pairs sorted by key. Note that this means that all of its keys must be
    comparable to each other; for instance you cannot have both 1 and '1' as keys, as integers and strings are not
    comparable."""
    
    
class SortedObject(_SortedMixin, OrderedObject):
    """An Object which keeps all of its attributes sorted. The usual [] notation can still be used as it can for regular
    Objects, but note that passing non-strings this way will not work in general, as these non-strings cannot be
    compared to the strings which the attributes are stored with, and thus no notion of sorting would make sense."""


class nonneg_indexing:
    def __getitem__(self, item):
        try:
            # In case :item: is a slice
            first_item = item.start
        except AttributeError:
            first_item = item

        if first_item < 0:
            raise IndexError('{} index out of range'.format(self.__class__))
        return super(nonneg_indexing, self).__getitem__(item)


class nonneg_deque(nonneg_indexing, collections.deque):
    """As collections.deque, but only supports positive indexing."""


class nonneg_list(nonneg_indexing, list):
    """As collections.deque, but only supports positive indexing."""


class qlist(nonneg_list):
    """A list which quietly ignores all IndexErrors, and only accepts non-negative indices. Useful to avoid
    having to write lots of try-except code to handle the edges of the list."""

    class Eater:
        """Used by qlist to quietly ignore anything chaining off of its result."""

        def __getattribute__(self, item):
            return self

        def __getitem__(self, item):
            return self

        def __call__(self, *args, **kwargs):
            return self

    def __init__(self, *args, except_val=Eater(), **kwargs):
        self.except_val = except_val
        super(qlist, self).__init__(*args, **kwargs)

    def __getitem__(self, item):
        try:
            val = super(qlist, self).__getitem__(item)
        except IndexError:
            val = self.except_val
        return val


class _delmixin:
    def __delitem__(self, key):
        try:
            super(_delmixin, self).__delitem__(key)
        except KeyError:
            pass


class deldict(_delmixin, dict):
    """A dictionary that doesn't mind about bad del attempts."""


class deldefaultdict(_delmixin, collections.defaultdict):
    """A collections.defaultdict that doesn't mind about bad del attempts."""


class ContainsAll:
    """Instances of this class always returns true when testing if something is contained in it."""
    def __contains__(self, item):
        return True


class ContainerMetaclass(type):
    def __contains__(cls, item):
        if cls is Container:
            return False
        if item in cls.__dict__.values():
            return True
        for parent_class in cls.__bases__:
            if item in parent_class:
                return True
        return False

    def __len__(self):
        length = 0
        for _ in self.items():
            length += 1
        return length

    def __getitem__(cls, item):
        return type(cls).__getattribute__(cls, item)

    def __setitem__(cls, key, value):
        type(cls).__setattr__(cls, key, value)

    def __delitem__(cls, key):
        type(cls).__delattr__(cls, key)

    def __iter__(cls):
        return cls.values()

    def items(cls):
        def parent_items():
            for parent in cls.__bases__:
                if parent is not Container:
                    for item in parent.items():
                        yield item
        for key, val in itertools.chain(cls.__dict__.items(), parent_items()):
            if not strings.is_magic(key):
                yield key, val

    def keys(cls):
        for key, val in cls.items():
            yield key

    def values(cls):
        for key, val in cls.items():
            yield val

    def __add__(cls, other):
        if isinstance(other, ContainerMetaclass):
            other_class = other
        else:  # Convert 'other' into a class we can inherit from
            class other_class(Container):
                pass
            for item in other:
                setattr(other_class, misc.uuid(), item)

        class ContainerCombined(cls, other_class):
            pass
        return ContainerCombined

    def __repr__(cls):
        arg_strs = []
        for key, val in cls.items():
            arg_strs.append(f'{key}={val}')
        kwargs = ', '.join(arg_strs)
        return f'{cls.__name__}({kwargs})'


class Container(metaclass=ContainerMetaclass):
    """Allows use of the 'in' keyword to test if the specified value is one of the values that one of its class
    variables is set to. Also provides keys(), values(), items() methods in a similar fashion to dicts. Containers can
    be added together, and can also have tuples and lists added to them. Finally they have use __(get|set|del)item__ in
    place of __(get|set|del)attr__, so they behave a bit like dictionaries. (In some sense a Container is the complement
    to objects.Object, which is a dictionary that behaves like a class.)

    Emphasis is placed on the fact that 'in' tests if the specified value is a _value_, not a key. (Unlike
    dictionaries.)

    Note that subclasses of Container should not be subclasses of anything else. (Unless the anything else is itself a
    subclass of Container; that's fine.)
    """
