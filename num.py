import math


def clamp(val, min_, max_):
    """Clamps :val: to the range between :min_: and :max_:"""
    return min(max(val, min_), max_)


def round_mult(val, multiple, direction='round'):
    """Rounds :val: to the nearest :multiple:. The argument :direction: should be either 'round', 'up', or 'down'."""
    round_func = {'round': round, 'up': math.ceil, 'down': math.floor}
    return round_func[direction](val / multiple) * multiple


def num_digits(n):
    """Returns the number of digits in an integer :n:.

    Source:
    https://stackoverflow.com/a/2189827
    """

    if n > 0:
        return int(math.log10(n)) + 1
    elif n == 0:
        return 1
    else:
        return int(math.log10(-n)) + 2


def math_eval(string, subs=None):
    """Evaluates a given string as a (real) mathematical expression, and returns its result. Is in theory done in a
    safe manner, allowing untrusted input to be passed as the :string: argument. (But not for the :subs: argument!)

    Arguments:
    :str string: A string for the expression to be evaluated, which may include math functions. e.g. '4', 'tanh(6)'.
        (The math functions do not have to be expressed as 'math.tanh' etc.) May also include other objects, in
        particular mathematical variables, e.g. 'x ** 2', provided a value is specified for these extra values via the
        :subs: argument.
    :subs: Should usually be a dictionary specifying what any extra things mean. e.g.
        '{"x": 4, "func": lambda x: math.sqrt(math.tanh(x))}' would allow for passing 'func(x)' as :string:. As this is
        most commonly used for specifying the value of some variable, if :subs: lacks the 'items' attribute, then it
        will be directly interpreted itself as the value for a variable named 'x'.

    Examples:
    >>> math_eval('tanh(1)')
    0.7615941559557649
    >>> math_eval('y', {'y': 5})
    5
    >>> math_eval('x ** 2', 4)
    16
    >>> import math
    >>> math_eval('func(x)', {'x': 4, 'func': lambda x: math.sqrt(math.tanh(x))})
    0.999664593620814
    """

    math_list = ['acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
                 'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp',
                 'hypot', 'ldexp', 'log', 'log10', 'modf', 'pi', 'pow',
                 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
    math_dict = {name: getattr(math, name) for name in math_list}
    math_dict['abs'] = abs
    if subs is not None:
        if hasattr(subs, 'items'):
            for key, val in subs.items():
                math_dict[key] = val
        else:
            math_dict['x'] = subs
    return eval(string, {'__builtins__': None}, math_dict)
