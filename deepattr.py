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