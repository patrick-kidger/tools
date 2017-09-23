"""Objects for storing data."""

import itertools

import Tools.tool_strings as tool_strings
import Tools.wrappers as wrappers


class Object(dict):
    """Subclasses dictionary to allow for using . notation to access its stored variables.
    
    The name is a reference to Objects in JavaScript, which behave in this way."""
    
    def __init__(self, *args, default_value=None, kwargs_={}, **kwargs):
        for default in args:
            self[default] = self._wrapper(default_value)
        for key, val in itertools.chain(kwargs.items(), kwargs_.items()):
            self[key] = self._wrapper(val)
        
    def _wrapper(self, input):
        return input
    
    def __getattr__(self, item):
        if self.is_magic(item):
            return super(Object, self).__getattr__(item)
        else:
            return self.__getitem__(item)
        
    def __setattr__(self, item, value):
        if self.is_magic(item):
            return super(Object, self).__setattr__(item)
        else:
            return self.__setitem__(item, value)
    
    def __delattr__(self, item):
        if self.is_magic(item):
            return super(Object, self).__delattr__(item)
        else:
            return self.__delitem__(item)
        
    @staticmethod
    def is_magic(item):
        return item.startswith('__') and item.startswith('__')
        
        
class PropObject(Object):
    """Subclasses Object so that accessing any of its values results in that value being called before
    being returned.
    
    Thus its intended that is variables will probably be lambda functions. The name is because its
    values are emulating @property."""
    
    def _wrapper(self, input):
        return wrappers.StrCallable(input)
    
    def __getitem__(self, item):
        return super(Object, self).__getitem__(item)()
        
        
class ContainerMetaclass(type):
    def __contains__(cls, item):
        if item in cls.__dict__.values():
            return True
        for parent_class in cls.__bases__:
            if parent_class is Container:
                return False
            if item in parent_class:
                return True
        return False


class Container(object, metaclass=ContainerMetaclass):
    """Allows use of the 'in' keyword to test if the specified value is one of
    the values that one of its class variables is set to."""

    
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
                    raise IndexError(tool_strings.QLIST_NON_NEGATIVE_ERROR)
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
