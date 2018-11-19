import sys


class CallableModuleBase:
    """Marks a module as being callable."""
    pass


def endow_attrs(name, attrs):
    """Makes the module with name :name: callable with the attributes specified in the dictionary :attrs:.

    For each (key, value) pair in attrs, the key should be the name of the attribute to add, and the value should be a
    function which takes the class of the new module, see the example below. (Being given the class makes doing super
    chains possible.)

    Example:
        >>> def _dir(cls):
        >>>     def __dir__(self):
        >>>         return super(cls, self).__dir() + ['some', 'other', 'stuff']
        >>> make_module_callable(__name__, {'__dir__': _dir})
    """

    old_cls = sys.modules[name].__class__

    class CallableModule(old_cls, CallableModuleBase):
        pass

    for key, val in attrs.items():
        setattr(CallableModule, key, val(CallableModule, old_cls))

    sys.modules[name].__class__ = CallableModule
