class ClassAdder(type):
    """Set as a metaclass to allow classes to be 'added' together to produce a subclass inheriting from both.

    Easily allows the use of multiple metaclasses, by 'adding' them together to create a new metaclass."""
    def __add__(self, other):
        class ClassesAdded(self, other):
            pass
        return ClassesAdded


class WithAnder(object):
    """Mixin to allow for adding classes used in with statements together.

    Example usage:

    >>> class A(WithAnder):
    ...     def __enter__(self):
    ...         pass
    ...     def __exit__(self, exc_type, exc_val, exc_tb):
    ...         pass
    ...
    >>> class B(WithAnder):
    ...     def __enter__(self):
    ...         pass
    ...     def __exit__(self, exc_type, exc_val, exc_tb):
    ...         pass
    ...
    >>> with A() + B():
    ...     pass
    """
    def __add__(self, other):
        class WithCombined(WithAnder):
            def __enter__(self_combined):
                self.__enter__()
                other.__enter__()

            def __exit__(self_combined, exc_type, exc_val, exc_tb):
                self.__exit__(exc_type, exc_val, exc_tb)
                other.__exit__(exc_type, exc_val, exc_tb)
        return WithCombined()


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
