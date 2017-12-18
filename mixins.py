import copy

import Tools.helpers as helpers
import Tools.objects as objects


class NoneAttributesMixin:
    """Accessing attributes which do not exist will return None instead of raising an AttributeError."""
    def __getattr__(self, item):
        return None


class DynamicSubclassingMixin:
    """Allows for dynamically setting the subclass of the instance. This function returns a class that should be
    inherited from.

    The class should have a dictionary called '_instance_properties', specifying (as keys) what properties it is
    expecting to have, along with their initial state (as values).

    This mixin will only usually actually be necessary when wishing to adjust non-method properties, as methods are
    (usually) actually class-level properties, and thus a simple self.__class__ = Foo statement would then suffice."""
    _instance_properties = dict()

    def __init__(self):
        for attr in self._instance_properties:
            setattr(self, attr, self._instance_properties[attr])
        super(DynamicSubclassingMixin, self).__init__()

    def set_subclass(self, subclass):
        """Sets the class of the instance to the specified subclass."""
        existing_class_attr_names = set(self._instance_properties.keys())
        new_instance_properties = subclass._instance_properties
        new_subclass_attr_names = set(new_instance_properties.keys())

        attrs_to_remove = existing_class_attr_names.difference(new_subclass_attr_names)
        attrs_to_add = new_subclass_attr_names.difference(existing_class_attr_names)

        for attr in attrs_to_remove:
            delattr(self, attr)
        for attr in attrs_to_add:
            setattr(self, attr, copy.deepcopy(new_instance_properties[attr]))

        self.__class__ = subclass


class FindableSubclassMixin:
    """Allows for locating a subclass based on a particular class variable being set to a particular value. It does a
    full search of the subclass structure each time its methods are called, which is not particular efficient. You may
    prefer the subclass_tracker function below."""

    @classmethod
    def all_subclasses(cls):
        """Generator for all subclasses, including subsubclasses etc. Includes this class itself at the start."""
        yield cls
        for subclass in cls.__subclasses__():
            # Don't yield subclass here, it'll come through as part of its all_subclasses call.
            for subsubclass in subclass.all_subclasses():
                yield subsubclass

    @classmethod
    def find_subclass(cls, attr_name, attr_given):
        """Finds a subclass based on a particular class variable being set to a particular value."""
        for subclass in cls.all_subclasses():
            cls_attr = getattr(subclass, attr_name)
            if cls_attr == attr_given:
                return subclass
        return cls


def subclass_tracker(attr_name):
    """Creates a class which will record all of its subclasses (and subsub, etc.) in a dictionary, and provides a
    function to look them up in this dictionary. The argument :attr_name: is the name of the attribute that its
    subclasses should specify; the value of this attribute is the key in this dictionary, with its value being the
    subclass it is associated with.

    *** Example usage **
    >>> class A(subclass_tracker('id_field')): id_field = 'id_str_for_A'
    ...
    >>> class B(A): id_field = 'id_str_for_B'
    ...
    >>> class C(A): id_field = 'id_str_for_C'
    ...
    >>> class D(B): id_field = 'id_str_for_D'
    ...
    >>> A.find_subclass('id_str_for_D')

    *** Details ***
    There is a single registry that can be accessed by all subclasses in the structure, and so
    >>> C.find_subclass('id_str_for_A')
    >>> C.find_subclass('id_str_for_B')
    will both work, and return A and B respectively.

    A subclass does not have to define an attribute with name :attr_name:. In this case it will just not be added to the
    registry, and will not be findable through this system.
    """

    class SubclassTrackerMixin:
        _subclass_registry = dict()

        def __init_subclass__(cls, **kwargs):
            super(SubclassTrackerMixin, cls).__init_subclass__(**kwargs)

            attr_value = getattr(cls, attr_name, None)
            # We might not set attr_name on some subclasses, perhaps because that subclass is itself an abstract base
            # class for its subclasses; doing so shouldn't overwrite what we already have.
            if attr_value not in SubclassTrackerMixin._subclass_registry and attr_value is not None:
                # We reference SubclassTrackerMixin explicitly here, rather than using cls, so that a class inheriting
                # from multiple trackers works.
                SubclassTrackerMixin._subclass_registry[attr_value] = cls

        @classmethod
        def find_subclass(cls, attr_value):
            """Finds the subclass associated with the specified attribute value."""
            return cls._subclass_registry[attr_value]

        @staticmethod
        def subclasses():
            # Returning a shallow copy
            return {key: val for key, val in SubclassTrackerMixin._subclass_registry.items()}

    return SubclassTrackerMixin


def dynamic_subclassing_by_attr(attr_name):
    """Combines dynamic subclassing with locating subclasses by attribute name."""

    class DynamicSubclassingByAttrMixin(DynamicSubclassingMixin, subclass_tracker(attr_name)):
        def pick_subclass(self, field_value):
            """Sets the class of the instance to the class associated with the inputted value."""
            cls = self.find_subclass(field_value)
            self.set_subclass(cls)

    return DynamicSubclassingByAttrMixin


class ContainerMetaclass(type):
    def __contains__(cls, item):
        if cls is Container:
            return False
        if item in cls.__dict__.values():
            return True
        for parent_class in cls.__bases__:
            if item in parent_class:
                return True
        return False

    def items(cls):
        for key, val in cls.__dict__.items():
            if not helpers.is_magic(key):
                yield key, val

    def keys(cls):
        for key in cls.__dict__.keys():
            if not helpers.is_magic(key):
                yield key

    def values(cls):
        for key, val in cls.items():
            yield val

    def __add__(cls, other):
        try:  # Test if 'other' is iterable. (i.e. is a tuple or list)
            iter(other)
        except TypeError:  # Assume other is a Container
            other_class = other
        else:  # Convert 'other' into a class we can inherit from
            class other_class(Container):
                pass
            for item in other:
                setattr(other_class, helpers.uuid(), item)

        class ContainerCombined(cls, other_class):
            pass
        return ContainerCombined


class Container(metaclass=ContainerMetaclass):
    """Allows use of the 'in' keyword to test if the specified value is one of the values that one of its class
    variables is set to. Also allows for use of 'in' to iterate over its elements. Containers can be added together,
    and can also have tuples and lists added to them."""


class ContainsAll:
    """Instances of this class always returns true when testing if something is contained in it."""
    def __contains__(self, item):
        return True


class HasXYPositionMixin:
    """Gives the class a notion of x, y position."""
    def __init__(self, pos=None):
        self.pos = objects.Object(x=0, y=0)
        if pos is not None:
            self.set_pos(pos)
        super(HasXYPositionMixin, self).__init__()

    def set_pos(self, pos):
        """Sets the object's current position"""
        self.pos.x = pos.x
        self.pos.y = pos.y

    @property
    def x(self):
        """The object's current x position."""
        return self.pos.x

    @property
    def y(self):
        """The object's current y position."""
        return self.pos.y

    @x.setter
    def x(self, val):
        self.pos.x = val

    @y.setter
    def y(self, val):
        self.pos.y = val


class HasPositionMixin(HasXYPositionMixin):
    """Gives the class a notion of x, y, z position."""
    def __init__(self, pos=None):
        self.pos = objects.Object(x=0, y=0, z=0)
        if pos is not None:
            self.set_pos(pos)
        # Deliberately calling the super of its base class; we're overwriting its __init__ here.
        super(HasXYPositionMixin, self).__init__()

    def set_pos(self, pos):
        super(HasPositionMixin, self).set_pos(pos)
        self.pos.z = pos.z

    @property
    def z(self):
        """The object's current z position."""
        return self.pos.z

    @z.setter
    def z(self, val):
        self.pos.z = val