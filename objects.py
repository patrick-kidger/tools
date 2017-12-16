"""Objects for storing data."""

import itertools
import collections

import Tools.helpers as helpers
import Tools.wrappers as wrappers


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
        dict_ = {var: default_value for var in args}
        return cls.from_dict(dict_)
    
    def __getattr__(self, item):
        if helpers.is_magic(item):
            super(_ObjectMixin, self).__getattr__(item)
        else:
            try:
                returnval = self.__getitem__(item)
            except KeyError as e:
                raise AttributeError(e) from e
            else:
                return returnval
        
    def __setattr__(self, item, value):
        if helpers.is_magic(item):
            super(_ObjectMixin, self).__setattr__(item, value)
        else:
            self.__setitem__(item, value)
    
    def __delattr__(self, item):
        if helpers.is_magic(item):
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
            if sorted([key, key_]) == [key, key_]:
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
    The name is a reference to Objects in JavaScript, which behave in this way."""


class SortedObject(_SortedMixin, Object):
    """An Object which keeps all of its attributes sorted. The usual [] notation can still be used as it can for regular
    Objects, but note that passing non-strings this way will not work in general, as these non-strings cannot be
    compared to the strings which the attributes are stored with, and thus no notion of sorting would make sense."""


class OrderedObject(_ObjectMixin, collections.OrderedDict):
    """An Object which remembers the order its attributes were added in."""


class SortedDict(_SortedMixin, collections.OrderedDict):
    """A dictionary which keeps its key: value pairs sorted by key. Note that this means that all of its keys must be
    comparable to each other; for instance you cannot have both 1 and '1' as keys, as integers and strings are not
    comparable."""


class PropObject(Object):
    """Subclasses Object so that accessing any of its values results in that value being called before
    being returned.

    Thus its intended that is variables will probably be lambda functions. The name is because its
    values are emulating @property."""

    def __getitem__(self, item):
        return super(Object, self).__getitem__(item)()

    def _wrapper(self, input_):
        return wrappers.StrCallable(input_)


class WithNothing:
    """Does nothing when used in a with statement. Example usage:

    >>> with DoesSomething() if condition else WithNothing():
    ...     some_stuff()
    """
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


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
