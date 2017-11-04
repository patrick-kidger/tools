"""Objects for storing data."""

import itertools
import collections

from . import _strings as _strings
from . import helpers as helpers
from . import wrappers as wrappers


class _ObjectMixin(object):
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
            return super(_ObjectMixin, self).__getattr__(item)
        else:
            return self.__getitem__(item)
        
    def __setattr__(self, item, value):
        if helpers.is_magic(item):
            return super(_ObjectMixin, self).__setattr__(item, value)
        else:
            return self.__setitem__(item, value)
    
    def __delattr__(self, item):
        if helpers.is_magic(item):
            return super(_ObjectMixin, self).__delattr__(item)
        else:
            return self.__delitem__(item)

    def _wrapper(self, input_):
        return input_


class _SortedMixin(object):
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


class WithNothing(object):
    """Does nothing when used in a with statement. Example usage:

    >>> with DoesSomething() if condition else WithNothing():
    ...     some_stuff()
    """
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    
class list_tuplable_index(list):
    """A list which may be indexed by tuple: it will take the first value in the tuple as
    the index within itself, and then pass the rest of the tuple for indexing within the
    selected element."""
    
    def __getitem__(self, item):
        try:
            first_item = item[0]
            remaining_items = item[1:]
        except TypeError:
            # The usual behaviour
            return super(list_tuplable_index, self).__getitem__(item)
        else:
            # Now try indexing by tuple.
            get_item = super(list_tuplable_index, self).__getitem__(first_item)
            return_item = get_item[remaining_items] if remaining_items else get_item
            return return_item
        
        
class qlist(list_tuplable_index):
    """A list which quietly ignores all IndexErrors, and only accepts non-negative indices. Useful to avoid
    having to write lots of try-except code to handle the edges of the list."""
    
    class Eater(object):
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
        # So that we can index by tuple
        try:
            first_item = item[0]
        except TypeError:
            first_item = item

        try:
            try:
                if first_item < 0:
                    raise IndexError(_strings.QLIST_NON_NEGATIVE_ERROR)
            except TypeError:  # If first_item is actually a slice or something
                pass
            val = super(qlist, self).__getitem__(item)
        except IndexError:
            val = self.except_val
        return val
        
        
def array(*args, fill_func=lambda pos: 0, list_type=list_tuplable_index, _pos=None):
    """Creates a list of lists of lists of..., of size as specified by its arguments.
    
    By default, the returned array may be indexed by tuple,
    i.e. myarray[1, 2, 3] == myarray[(1, 2, 3)] == myarray[1][2][3].
    This may change depending on list_type.
    
    e.g. array(2, 3, 4) produces a list of two lists, each comprising of three lists, each comprising of four lists.
    
    Also accepts a 'fill_func' argument, which is a function which will be called to populate the elements of the bottom
    lists. (It's a function because otherwise e.g. fill=Tile() would use the same instance of Tile everywhere.) The function
    will have its position within the array passed as an argument.
    
    Also accepts a 'list_type' argument, which is what every list will be converted to. E.g. to use qlist above.
    
    The '_pos' argument is used in internal recursive calls and should not be used."""
    
    if _pos is None:
        _pos = []
    if len(args):
        length = args[0]
        wrapped_array = [array(*args[1:], fill_func=fill_func, list_type=list_type, _pos=_pos + [i]) for i in range(length)]
        return list_type(wrapped_array)
    else:
        return fill_func(tuple(_pos))
