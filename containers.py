"""Objects for storing data."""

import collections
import weakref

from . import strings


class Record:
    """Creates a record datatype, roughly equivalent to a mutable tuple with named entries.

    It differs from collections.namedtuple in that (a) entries are mutable, and (b) it does not need to be defined
    first; we can simply create it from the get-go. (This is also its main difference over something like the PyRecord
    project. Lastly (c) entries are not accessible via indexing. It can also be thought of as a counterpart to Object,
    except that Object allows for [] notation lookup, and allows for the addition of other entries.

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

    If you really want to define it first then see the Record.spec method.
    """
    __slots__ = ()
    _record_subclasses = weakref.WeakValueDictionary()

    # Minor hackery incoming.
    # We do it this way so that the following works as you'd expect:
    # >>> r = Record(x=4, y=5)
    # >>> assert isinstance(r, Record)
    # Also so that subclassing Record is also (reasonably) safe.
    def __new__(cls, *args, **kwargs):
        """
        Used to create and instantiate a class for recording data in slots. See Record.__doc__ for more information.

        Any :*args: should be strings specifying the name of a slot. Any :**kwargs: should have the name of the slot as
        the name of the keyword argument, and the default value of the slot as its value.

        e.g.
        >>> r = Record('z', x=4, y=5)
        Which might represent the (4, 5) coordinate in 2-dimensional space, and allow for setting a z coordinate later,
        if desired.

        See also the Record.spec method if you don't want to instantiate immediately.
        """

        if hasattr(cls, '_skip_record'):
            return super(Record, cls).__new__(cls)

        slots = (*args, *kwargs.keys())
        try:
            # Reuse existing classes with the correct slots if they exist.
            # Note that they need not have the correct defaults, but that doesn't matter - the requested values will be
            # set in __init__ anyway.
            _Record = cls._record_subclasses[slots]
        except KeyError:
            _Record = cls.spec(*args, **kwargs)
            # Store the class so we can reuse it later; no need to create a new subclass for every instance.
            # The assumption is that if someone is creating a subclass via Record.spec then they can handle such things
            # themselves, the same way one would with any other class. But when just doing Record(...), they're not
            # going to - and it's probably better to avoid creating a a lot of classes than it is to worry about them
            # doing strange things with the shared classes afterwards.
            cls._record_subclasses[slots] = _Record

        return super(Record, _Record).__new__(_Record)

    def __init_subclass__(cls, **kwargs):
        super(Record, cls).__init_subclass__(**kwargs)
        # If we're creating a subclass of Record in the usual way for classes...
        if not hasattr(cls, '_skip_record'):
            # ...then give it somewhere to store its own 'extra subclasses' that it creates in __new__
            cls._record_subclasses = weakref.WeakValueDictionary()

    def __init__(self, *args, **kwargs):
        # There's two different ways to end up in __init__ for this class.

        # Firstly, one can instantiate a class the usual way:
        # >>> myrecord = Record('x', y=4)
        # In which case the machinery in __new__, above, will dynamically create a subclass of Record and actually use
        # that. If that is the case, then the same args and kwargs will be passed to both __new__ and __init__.
        # __new__ may end up creating a new class with _defaults set to kwargs, or it may reuse an existing class with
        # the correct slots, in which case the _defaults may be wrong - but that won't matter, because the args and
        # kwargs will be passed through here, and we just set their values to exactly what we want.

        # Secondly, one could first define a class:
        # >>> record_class = Record.spec('x', y=4)
        # and then instantiate it:
        # >>> myrecord = record_class()
        # perhaps with some args or kwargs:
        # >>> myrecord = record_class('y', x=2)
        # In this case, the __new__ machinery is bypassed by setting _skip_record in Record.spec, so the class doesn't
        # get recorded. So we can now trust that the _defaults really are what we want them to be, and is what should be
        # used - unless someone explicitly wants an empty field by passing it as an arg when initialising.

        # Either way, this does precisely what we want. (It's true that that's not entirely clear; might come back and
        # rewrite this at some point for clarity.)
        for key, val in self._defaults.items():
            if key not in args and key not in kwargs:
                kwargs[key] = val
        for key, val in kwargs.items():
            setattr(self, key, val)
        super(Record, self).__init__()

    @classmethod
    def spec(cls, *args, **kwargs):
        """Used to create, but not instantiate, a class; otherwise see Record.__doc__ and Record.__new__.__doc__ for
        more information.

        This method basically allows you to create a class with the slots equal to (*args, *kwargs.keys()), and which
        when instantiated, will have the slots corresponding to the kwargs automatically populated with the values of
        kwargs.values(). (Although these can be overridden when instantiated, even to not have any value at all, by
        passing them as an arg when instantiating.)

        Example (note how slots without values are printed):
        >>> r = Record.spec('r', 'g', b=3, k=2)
        >>> r()
        Record(r=, g=, b=3, k=2)
        >>> r('b', r=2, k=4)
        Record(r=2, g=, b=, k=4)

        If you want more complicated things in your data containers - validators, default values populated by factory
        functions, etc, then check out the attrs project, or the dataclass stdlib in Py3.7+.
        """

        slots = (*args, *kwargs.keys())
        # Create a class like this so that we don't have to mess around setting __name__ and __qualname__ manually.
        # Set the __slots__ attribute to do what we want in the first place.
        # Set the _defaults attribute to store the default parameters for our slots
        # Set the _skip_record attribute so that we can detect that this isn't an abstract base class inheriting
        #   from Record, but is in fact one of our own on-the-fly subclasses.
        dict_ = {'__slots__': slots, '_defaults': kwargs, '_skip_record': None}
        return type(cls.__name__, (cls,), dict_)

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
            try:
                val = repr(getattr(self, key))
            except AttributeError:
                # In case a value gets del'd
                val = ''
            arg_strs.append(f'{key}={val}')
        kwargs = ', '.join(arg_strs)
        return f'{self.__class__.__name__}({kwargs})'

    def __getitem__(self, item):
        try:
            return self.__getattribute__(item)
        except AttributeError as e:
            raise KeyError(e) from e

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __delitem__(self, key):
        try:
            self.__delattr__(key)
        except AttributeError as e:
            raise KeyError(e) from e

    def update(self, other, ignore_extra=False):
        """Update this Record with the values from another Record. If :ignore_extra: is True, then any extra attributes
        in the other Record without a corresponding attribute in this Record will not raise an error.
        """
        for key in other.__slots__:
            try:
                val = getattr(self, key)
            except AttributeError:
                # An attribute may get del'd
                pass
            else:
                if ignore_extra:
                    try:
                        setattr(self, key, val)
                    except AttributeError:
                        pass
                else:
                    setattr(self, key, val)



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
                return self.__getitem__(item)
            except KeyError as e:
                raise AttributeError(e) from e
        
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
