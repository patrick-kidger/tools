import itertools
import re
import uuid as uuid_


def _getattritem(o, name):
    if len(name) > 1 and ']' == name[-1]:
        return o[int(name[:-1])]
    else:
        return getattr(o, name)


def _setattritem(o, name, val):
    if len(name) > 1 and ']' == name[-1]:
        o[int(name[:-1])] = val
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


def deepgetattr(top_object, variable_name):
    """Use as getattr, but can find subattributes separated by a '.', e.g. deepgetattr(a, 'b.c'). Also supports access
    via __getitem__ notation for integers, e.g. deepgetattr(a, 'b.c[5].e')"""
    penultimate_variable, last_variable_name = deep_locate_variable(top_object, variable_name)
    return _getattritem(penultimate_variable, last_variable_name)


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


__sentinel = object()
def extract_keys(dict, keys, no_key_val=__sentinel):
    """Removes the specified keys from the given dictionary, and returns a dictionary containing those key:value
    pairs. Default behaviour is to ignore those keys which can't be found in the original dictionary. The optional
    argument :no_key_val: can be set to what value missing keys should take in the returned dictionary."""

    return_dict = {}
    for key in keys:
        val = dict.pop(key, no_key_val)
        if val is not __sentinel:
            return_dict[key] = val
    return return_dict


def clamp(val, min_, max_):
    """Clamps :val: to the range between :min_: and :max_:"""
    return min(max(val, min_), max_)


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
