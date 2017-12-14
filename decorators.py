import functools


def register(name_str, registration_dict):
    """A decorator which registers the decorated object in the specified dictionary."""

    def wrapper(input_val):
        registration_dict[name_str] = input_val
        return input_val
    return wrapper


def record(registration_list):
    """A decorator which records the decorated object in the specified list."""

    def wrapper(input_val):
        registration_list.append(input_val)
        return input_val
    return wrapper


class combomethod:
    """Marks the decorated method as being usable as both an instance method and a class method."""

    def __init__(self, method):
        self.method = method

    def __get__(self, instance, owner):
        @functools.wraps(self.method)
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
