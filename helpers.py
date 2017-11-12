import uuid as uuid_


def deep_locate_variable(top_object, variable_name):
    """Used to extend getattr etc. to finding subattributes."""
    variable_descent = variable_name.split('.')
    prev_variable = top_object
    while len(variable_descent) > 1:
        next_variable_name = variable_descent.pop(0)
        prev_variable = deepgetattr(prev_variable, next_variable_name)
    return prev_variable, variable_descent[0]


def deepgetattr(top_object, variable_name):
    """Use as getattr, but can find subattributes separated by a '.', e.g. deepgetattr(a, 'b.c')"""
    penultimate_variable, last_variable_name = deep_locate_variable(top_object, variable_name)
    return getattr(penultimate_variable, last_variable_name)


def deepsetattr(top_object, variable_name, value):
    """Use as setattr, but can find subattributes separated by a '.', e.g. deepsetattr(a, 'b.c')"""
    penultimate_variable, last_variable_name = deep_locate_variable(top_object, variable_name)
    setattr(penultimate_variable, last_variable_name, value)


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
