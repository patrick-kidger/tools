class ClassAdder(type):
    """Set as a metaclass to allow classes to be 'added' together to produce a subclass inheriting from both.

    Example usage:
    >>> class MetaA(object, metaclass=ClassAdder): pass
    >>> class MetaB(object, metaclass=ClassAdder): pass
    >>> class A(object, metaclass=MetaA): pass
    >>> class B(object, metaclass=MetaB): pass
    >>> class C(A, B, metaclass=A.__class__ + B.__class__): pass
    """
    def __add__(self, other):
        class ClassesAdded(self, other):
            pass
        return ClassesAdded
