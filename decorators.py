import functools as ft
import inspect


def register(registration_dict, name_str=None):
    """A decorator which registers the decorated object in the specified dictionary."""

    def wrapper(input_val):
        if name_str is None:
            name_str_ = input_val.__name__
        else:
            name_str_ = name_str
        registration_dict[name_str_] = input_val
        return input_val
    return wrapper


def record(registration_list):
    """A decorator which records the decorated object in the specified list."""

    def wrapper(input_val):
        registration_list.append(input_val)
        return input_val
    return wrapper


# Unlike functools.wraps, this just takes a name, not an existing function
def rename(funcname):
    """Renames a function to take on the new :funcname:. Modifies __name__ and __qualname__. Use as a decorator:

    >>> @rename('bob')
    ... def janet():
    ...     pass
    >>> janet.__name__
    'bob'
    """
    def _rename(func):
        if funcname is not None:
            func.__name__ = funcname
            loc = func.__qualname__.rsplit('.', 1)[0]
            func.__qualname__ = f'{loc}.{funcname}'
        return func
    return _rename


def with_defaults(defaults):
    """Modifies a function to use new default values.

    The argument :defaults: should be a dictionary (or similar, such as an Object or Record), mapping argument names to
    default values. Note that with_defaults modifies the existing function in-place; it does not copy its input before
    modifying and returning it.

    For example:
    >>> @with_defaults({'a': 4})
    ... def myfunc(a):
    ...     print(a)
    >>> myfunc()
    4

    It is expected to use this to set default values for multiple functions in a DRY manner:
    >>> defaults = {'a': 4, 'b': 'hello', 'c': 7)
    >>> with_my_defaults = with_defaults(defaults)
    >>> @with_my_defaults
    ... def func1(a, b, c):
    ...     return a, b, c
    >>> func1()
    (4, 'hello', 7)

    Arguments not present (in this case there is no 'b' or 'c' argument) are simply not used:
    >>> @with_my_defaults
    ... def func2(a):
    ...     return a
    >>> func2()
    4

    Default arguments already in the function will not be overridden:
    >>> @with_my_defaults
    ... def func3(a, b=3):
    ...     return a, b
    >>> func3()
    (4, 3)

    Keyword-only arguments are handled:
    >>> @with_my_defaults
    ... def func4(a, *, c):
    ...     return a, c
    >>> func4()
    (4, 7)
    >>> @with_my_defaults
    ... def func5(a, *, d):
    ...     return a, d
    >>> func5(d=7)  # Will raise a TypeError as expected, if called without specifying the value of d
    (4, 7)

    Arguments without defaults cannot exist to the right of arguments with defaults, as usual:
    >>> @with_my_defaults
    ... def func6(a, z):
    ...    pass
    ValueError: Attempted to specify default argument 'a' before non-default argument.

    Finally multiple decorators may be applied to the same function, (provided they are done in such an order than at no
    point is an argument without defaults to the right of an argument with defaults):
    >>> @with_defaults({'a': 3})
    ... @with_defaults({'b': 2})
    ... def f(a, b):
    ...     return a, b
    >>> f()
    (3, 2)
    """

    def with_defaults_decorator(func):
        argspec = inspect.getfullargspec(func)

        # First we handle the non-keyword-only arguments. These are the default arguments, from right to left
        arg_defaults = argspec.defaults
        arg_defaults = tuple() if arg_defaults is None else arg_defaults
        # Ignore arguments that already have default values specified
        # Cannot just use negative indexing here in case len(defaults) == 0
        args = argspec.args
        args = argspec.args[:len(args) - len(arg_defaults)]
        extra_defaults = []
        stopped_defaults = False
        for arg in reversed(args):  # Work backwards through the remaining arguments assigning default values
            try:
                arg_default = defaults[arg]
            except KeyError:
                # We've stopped assigning defaults. Trying to assign a default after this is an error, as one cannot
                # have a default argument specified before a non-default argument.
                stopped_defaults = True
            else:
                if stopped_defaults:
                    raise ValueError(f"Attempted to specify default argument '{arg}' before non-default argument.")
                extra_defaults.append(arg_default)
        func.__defaults__ = (*reversed(extra_defaults), *arg_defaults)

        # Now work through the keyword-only arguments
        kwonlyargs = argspec.kwonlyargs
        kwonlydefaults = argspec.kwonlydefaults
        kwonlydefaults = {} if kwonlydefaults is None else kwonlydefaults
        for kwarg in kwonlyargs:
            # Ignore arguments that already have default values specified
            if kwarg not in kwonlydefaults:
                try:
                    new_default = defaults[kwarg]
                except KeyError:
                    pass
                else:
                    if not func.__kwdefaults__:
                        func.__kwdefaults__ = {}
                    func.__kwdefaults__[kwarg] = new_default
        return func

    return with_defaults_decorator


class combomethod:
    """Marks the decorated method as being usable as both an instance method and a class method."""

    def __init__(self, method):
        self.method = method

    def __get__(self, instance, owner):
        @ft.wraps(self.method)
        def wrapper(*args, **kwargs):
            if instance is not None:
                return self.method(instance, *args, **kwargs)
            else:
                return self.method(owner, *args, **kwargs)
        return wrapper


class classproperty:
    """As @classmethod, but defines a class property instead. (It's closer to @classmethod than @property, as we don't
    define a __set__ method, etc.)"""

    def __init__(self, method):
        self.method = method

    def __get__(self, instance, owner):
        return self.method(owner)
