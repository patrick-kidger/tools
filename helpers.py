import itertools
import math
import random
import re
import uuid as uuid_


_sentinel = object()


def _getattritem(o, name):
    if len(name) > 1 and ']' == name[-1]:
        try:
            return o[int(name[:-1])]
        except (TypeError, IndexError) as e:
            raise AttributeError(e) from e
    else:
        return getattr(o, name)


def _setattritem(o, name, val):
    if len(name) > 1 and ']' == name[-1]:
        try:
            o[int(name[:-1])] = val
        except (TypeError, KeyError) as e:
            raise AttributeError(e) from e
    else:
        setattr(o, name, val)


def deep_locate_variable(top_object, variable_name):
    """Used to extend getattr etc. to finding subattributes."""
    _variable_descent = variable_name.split('.')
    variable_descent = []
    for var in _variable_descent:
        variable_descent.extend(var.split('['))

    next_variable = top_object
    for next_variable_name in variable_descent[:-1]:
        next_variable = _getattritem(next_variable, next_variable_name)
    return next_variable, variable_descent[-1]


def deepgetattr(top_object, variable_name, default=None):
    """Use as getattr, but can find subattributes separated by a '.', e.g. deepgetattr(a, 'b.c'). Also supports access
    via __getitem__ notation for integers, e.g. deepgetattr(a, 'b.c[5].e')"""

    try:
        penultimate_variable, last_variable_name = deep_locate_variable(top_object, variable_name)
        return _getattritem(penultimate_variable, last_variable_name)
    except AttributeError:
        if default is None:
            raise
        else:
            return default


def deepsetattr(top_object, variable_name, value):
    """Use as setattr, but can find subattributes separated by a '.', e.g. deepsetattr(a, 'b.c'). Also supports access
    via __getitem__ notation for integers, e.g. deepsetattr(a, 'b.c[5].e', some_val)"""
    penultimate_variable, last_variable_name = deep_locate_variable(top_object, variable_name)
    _setattritem(penultimate_variable, last_variable_name, value)


def uuid():
    """Returns a unique identifier in hex."""
    return uuid_.uuid4().hex


def is_magic(item):
    """Whether or not the specified string is __magic__"""
    return item.startswith('__') and item.startswith('__')


def extract_keys(dict, keys, no_key_val=_sentinel):
    """Removes the specified keys from the given dictionary, and returns a dictionary containing those key:value
    pairs. Default behaviour is to ignore those keys which can't be found in the original dictionary. The optional
    argument :no_key_val: can be set to what value missing keys should take in the returned dictionary."""

    return_dict = {}
    for key in keys:
        val = dict.pop(key, no_key_val)
        if val is not _sentinel:
            return_dict[key] = val
    return return_dict
    

def update_without_overwrite(dict1, dict2):
    """As dict.update, except that existing keys in :dict1: are not overwritten with matching keys in :dict2:."""
    for k, v in dict2.items():
        if k not in dict1:
            dict1[k] = v


def clamp(val, min_, max_):
    """Clamps :val: to the range between :min_: and :max_:"""
    return min(max(val, min_), max_)


def round_mult(val, multiple, direction='round'):
    """Rounds :val: to the nearest :multiple:. The argument :direction: should be either 'round', 'up', or 'down'."""
    round_func = {'round': round, 'up': math.ceil, 'down': math.floor}
    return round_func[direction](val / multiple) * multiple


def re_sub_recursive(pattern, sub, inputstr):
    """Recursive regex.

    :str pattern: The regex pattern
    :str sub: What to substitute the regex pattern for.
    :str inputstr: The string to perform the substitutions on."""
    patt = re.compile(pattern)

    old_inputstr = inputstr
    inputstr = patt.sub(sub, inputstr)
    while old_inputstr != inputstr:
        old_inputstr = inputstr
        inputstr = patt.sub(sub, inputstr)

    return inputstr


def single_true(iterable):
    """Checks that precisely one element of the iterable is truthy."""
    i = iter(iterable)
    return any(i) and not any(i)


def slice_pieces(sliceable, length):
    """Cuts a sliceable object into pieces of length 'length', and yields them one at a time."""
    if not sliceable:
        yield sliceable
    while sliceable:
        piece, sliceable = sliceable[:length], sliceable[length:]
        yield piece


def find_nth(haystack, needle, n):
    """Finds the nth occurrence of a substring 'needle' in a larger string 'haystack'."""
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start

    
def random_function(*args):
    """Picks one of its arguments uniformly at random, calls it, and returns the result.
    
    Example usage:
    >>> random_function(lambda: numpy.uniform(-2, -1), lambda: numpy.uniform(1, 2))
    """
    
    choice = random.randint(0, len(args) - 1)
    return args[choice]()

    
def split(delimiters, string, maxsplit=0):
    """Splits a :string: on multiple :delimiters:.
    
    Source:
    https://stackoverflow.com/a/13184791
    """
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)
