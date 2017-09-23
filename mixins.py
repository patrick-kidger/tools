import copy
        
        
class FindableSubclassMixin(object):
    """Allows for locating a subclass based on a particular class variable being set to a particular value."""
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
        """Finds a subclass based on a particular class variable being set to
        a particular value."""
        for subclass in cls.all_subclasses():
            cls_attr = getattr(subclass, attr_name)
            if cls_attr == attr_given:
                return subclass
        return cls


class DynamicSubclassingMixin(FindableSubclassMixin):
    """Allows for dynamically setting the subclass of the instance.

    The class should have a dictionary called '_subclass_properties', specifying (as keys) what properties
    it is expecting to have, along with their initial state (as values).

    This mixin will only usually actually be necessary when wishing to add non-method properties, as
    methods are (usually) actually class-level properties, and thus a simple self.__class__ = Foo statement
    would then suffice."""

    _subclass_properties = dict()

    def __init__(self):
        for attr in self._subclass_properties:
            setattr(self, attr, self._subclass_properties[attr])

    def set_subclass(self, subclass):
        """Sets the class of the instance to the specified subclass."""
        existing_class_attr_names = set(self._subclass_properties.keys())
        new_subclass_properties = subclass._subclass_properties
        new_subclass_attr_names = set(new_subclass_properties.keys())

        attrs_to_remove = existing_class_attr_names.difference(new_subclass_attr_names)
        attrs_to_add = new_subclass_attr_names.difference(existing_class_attr_names)

        for attr in attrs_to_remove:
            delattr(self, attr)
        for attr in attrs_to_add:
            setattr(self, attr, copy.deepcopy(new_subclass_properties[attr]))

        self.__class__ = subclass

    def pick_subclass(self, attr_name, attr_given, base_class):
        """Sets the class of the instance based on a particular class variable
        being set to a particular value."""
        cls = base_class.find_subclass(attr_name, attr_given)
        self.set_subclass(cls)
        
        
class NoneAttributesMixin(object):
    """Accessing attributes which do not exist will return None instead of raising an AttributeError."""
    def __getattr__(self, item):
        return None
