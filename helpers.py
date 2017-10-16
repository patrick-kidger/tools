class ClassAdder(type):
    """Set as a metaclass to allow classes to be 'added' together to produce a subclass inheriting from both.

    Easily allows the use of multiple metaclasses, by 'adding' them together to create a new metaclass."""
    def __add__(self, other):
        class ClassesAdded(self, other):
            pass
        return ClassesAdded
