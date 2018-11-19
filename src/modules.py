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
        >>> def __call__(self):
        >>>     return 42
        >>> endow_attrs(__name__, {'__call__': __call__})
    """

    module = sys.modules[name]
    old_cls = module.__class__

    class CallableModule(old_cls, CallableModuleBase):
        pass
    for key, val in attrs.items():
        setattr(CallableModule, key, val)
    module.__class__ = CallableModule
    return module, old_cls
