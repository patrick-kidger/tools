import functools as ft
import inspect
import typing


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

    This decorator may seem a tiny bit magic. Use with care.

    For example:
    >>> @with_defaults({'a': 4})
    ... def myfunc(a):
    ...     return a
    >>> myfunc()
    4

    It is expected to use this to set default values for multiple functions in a DRY manner:
    >>> defaults = {'a': 4, 'b': 'hello', 'c': 7}
    >>> with_my_defaults = with_defaults(defaults)
    >>> @with_my_defaults
    ... def func1(a, b, c):
    ...     # do something
    ...     return a, b, c
    >>> @with_my_defaults
    ... def func1_another(a, b, c):
    ...     # do something else; perhaps call func1 without needing to worry about keeping their default values in sync.
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

    Multiple decorators may be applied to the same function, (provided they are done in such an order than at no point
    is an argument without defaults to the right of an argument with defaults, although this restriction may be
    circumvented by using AliasDefault or HasDefault, as in the examples below):
    >>> @with_defaults({'a': 3})
    ... @with_defaults({'b': 2})
    ... def f(a, b):
    ...     return a, b
    >>> f()
    (3, 2)

    An argument may take on the default value assigned to another argument, by using AliasDefault:
    >>> @with_defaults({'a': 3})
    ... def f(b=AliasDefault('a')):
    ...     return b
    >>> f()
    3

    If this results in an argument with a default lying to the left of an argument without a default in the original
    function, then this may be solved by adding fake aliases: ```x=AliasDefault('x')``` or by using HasDefault.
    (Although it is probably better to reorder the arguments instead):
    >>> @with_defaults({'a': 3, 'x': 2})
    ... def f(b=AliasDefault('a'), 'x'=HasDefault):
    ...     return b, x
    >>> f()
    (3, 2)

    As using with_defaults means that it is not necessarily clear which arguments actually have default values, then
    arguments which have their default values supplied by a call to with_defaults may be marked as such by giving them
    the default value of HasDefault. This isn't enforced - with_defaults will leave it as a default value if no default
    value is supplied, as of course it might be provided by a later call to with_defaults. It is simply a default value
    that with_defaults is happy to override. It provides a way to mark that an argument is using a default value. (Thus
    ```x=HasDefault``` functions the same as ```x=AliasDefault('x')```.
    """

    def with_defaults_decorator(func):
        argspec = inspect.getfullargspec(func)

        # First we handle the non-keyword-only arguments, from right to left.
        args = iter(reversed(argspec.args))
        arg_defaults = argspec.defaults
        arg_defaults = iter(reversed(tuple() if arg_defaults is None else arg_defaults))

        new_defaults = []
        stopped_defaults = False

        # First iterate through everything that already has a default
        for arg_default, arg in zip(arg_defaults, args):  # Shorter iterator must come first in zip
            if isinstance(arg_default, AliasDefault):
                # Use 'renamed' variable
                try:
                    new_default = defaults[arg_default.name]
                except KeyError:
                    # Keep the AliasDefault
                    new_default = arg_default
            elif isinstance(arg_default, _HasDefaultClass):
                try:
                    new_default = defaults[arg]
                except KeyError:
                    # Keep the HasDefault
                    new_default = arg_default
            else:
                # Use existing default
                new_default = arg_default

            new_defaults.append(new_default)

        # Now iterate through everything without a default
        for arg in args:
            try:
                new_default = defaults[arg]
            except KeyError:
                # We've stopped assigning defaults. Trying to assign a default after this is an error, as one cannot
                # have a default argument specified before a non-default argument.
                stopped_defaults = True
                continue
            else:
                if stopped_defaults:
                    raise ValueError(f"Attempted to specify default argument '{arg}' before non-default argument.")

            new_defaults.append(new_default)

        func.__defaults__ = tuple(reversed(new_defaults))

        # Now work through the keyword-only arguments
        kwonlydefaults = argspec.kwonlydefaults
        kwonlydefaults = {} if kwonlydefaults is None else kwonlydefaults
        for kwarg in argspec.kwonlyargs:
            # Ignore arguments that already have default values specified
            try:
                kwargval = kwonlydefaults[kwarg]
            except KeyError:
                try_to_get_default = True
            else:
                if isinstance(kwargval, AliasDefault):
                    kwarg = kwargval.name
                    try_to_get_default = True
                elif isinstance(kwargval, _HasDefaultClass):
                    try_to_get_default = True
                else:
                    try_to_get_default = False

            if try_to_get_default:
                try:
                    new_default = defaults[kwarg]
                except KeyError:
                    pass
                else:
                    # We do this check here, rather than once at the start, so that we don't assign to __kwdefaults__
                    # if we're not setting any of them. (As it's None by default.)
                    if not func.__kwdefaults__:
                        func.__kwdefaults__ = {}
                    func.__kwdefaults__[kwarg] = new_default
        return func

    return with_defaults_decorator


class AliasDefault:
    """Used to 'rename' an argument; see the documentation of with_defaults."""
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name


class _HasDefaultClass:
    """Used to mark an argument as having its default value supplied by a call to with_defaults.

    It acts as a default value that with_defaults is happy to override (normally it will leave existing default values
    alone.) Thus its purpose is simply for code clarity, to mark that a particular argument does have a default value
    specified.
    """


HasDefault = _HasDefaultClass()


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
