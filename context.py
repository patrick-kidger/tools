from . import deepattr


class WithAdder:
    """Mixin to allow for adding classes used in with statements together.

    Example usage:

    >>> class A(WithAdder):
    ...     def __enter__(self):
    ...         pass
    ...     def __exit__(self, exc_type, exc_val, exc_tb):
    ...         pass
    ...
    >>> class B(WithAdder):
    ...     def __enter__(self):
    ...         pass
    ...     def __exit__(self, exc_type, exc_val, exc_tb):
    ...         pass
    ...
    >>> with A() + B():
    ...     pass
    """
    def __add__(self, other):
        class WithCombined(WithAdder):
            def __enter__(self_combined):
                self.__enter__()
                other.__enter__()

            def __exit__(self_combined, exc_type, exc_val, exc_tb):
                self.__exit__(exc_type, exc_val, exc_tb)
                other.__exit__(exc_type, exc_val, exc_tb)
        return WithCombined()


def set_context_variables(owner, variable_names, value=True, callback=lambda: None):
    """Allows for easily creating objects to be used in 'with' statements, which set particular variables to particular
    values inside the context. Can also have an optional callback called on __exit__.

    Example usage:
    >>> class MyClass(object):
    ...     def __init__(self):
    ...         self.something = False
    ...     def with_something(self):
    ...         return set_context_variable(self, ('something',))
    ...
    >>> x = MyClass()
    >>> with x.with_something():
    ...     pass
    """

    class VariableSetter(WithAdder):
        def __enter__(self):
            self.old_variable_values = {}
            for variable_name in variable_names:
                self.old_variable_values[variable_name] = deepattr.deepgetattr(owner, variable_name)
                deepattr.deepsetattr(owner, variable_name, value)

        def __exit__(self, exc_type, exc_val, exc_tb):
            for variable_name in variable_names:
                deepattr.deepsetattr(owner, variable_name, self.old_variable_values[variable_name])
            callback()

    return VariableSetter()


class WithNothing:
    """Does nothing when used in a with statement. Example usage:
    >>> with DoesSomething() if condition else WithNothing():
    ...     some_stuff()
    """
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
