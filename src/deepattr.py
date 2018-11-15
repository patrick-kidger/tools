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


def _delattritem(o, name):
    if len(name) > 1 and ']' == name[-1]:
        try:
            del o[int(name[:-1])]
        except (TypeError, KeyError) as e:
            raise AttributeError(e) from e
    else:
        delattr(o, name)


def _deep_locate_variable(o, name):
    """Used to extend getattr etc. to finding subattributes."""
    _variable_descent = name.split('.')
    variable_descent = []
    for var in _variable_descent:
        variable_descent.extend(var.split('['))

    next_variable = o
    for next_variable_name in variable_descent[:-1]:
        next_variable = _getattritem(next_variable, next_variable_name)
    return next_variable, variable_descent[-1]


# TODO: Extend the __getitem__ notation to support arbitrary python objects. Will need to add an extra argument that
# TODO: provides a dictionary explaininng how to interpret such objects. (At the very least provide support for all
# TODO: python literals)
def deepgetattr(o, name, default=None):
    """Use as getattr, but can find subattributes separated by a '.'. Also supports access via __getitem__ notation for
    integers.

    Examples:
        >>> deepgetattr(a, 'b.c')
        >>> deepgetattr(a, 'b.c[5].e')
    """

    try:
        penultimate_variable, last_variable_name = _deep_locate_variable(o, name)
        return _getattritem(penultimate_variable, last_variable_name)
    except AttributeError:
        if default is None:
            raise
        else:
            return default


def deephasattr(o, name):
    """Use as getattr, but can check subattributes separated by a '.'. Also supports access via __getitem__ notation for
    integers.

    Examples:
        >>> deephasattr(a, 'b.c')
        >>> deephasattr(a, 'b.c[5].e')
    """
    try:
        deepgetattr(o, name)
    except AttributeError:
        return False
    else:
        return True


def deepsetattr(o, name, value):
    """Use as setattr, but can set subattributes separated by a '.'. Also supports access via __getitem__ notation for
    integers.

    Examples:
        >>> deepsetattr(a, 'b.c', 3)
        >>> deepsetattr(a, 'b.c[5].e', 'hello')
    """
    penultimate_variable, last_variable_name = _deep_locate_variable(o, name)
    _setattritem(penultimate_variable, last_variable_name, value)


def deepdelattr(o, name):
    """Use as delattr, but can delete subattributes separated by a '.'. Also supports access via __getitem__ notation
    for integers.

    Examples:
        >>> deepdelattr(a, 'b.c')
        >>> deepdelattr(a, 'b.c[5].e')
    """
    penultimate_variable, last_variable_name = _deep_locate_variable(o, name)
    _delattritem(penultimate_variable, last_variable_name)
