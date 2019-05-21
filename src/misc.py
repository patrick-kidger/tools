import inspect
import os
import random
import string
import uuid as uuid_


def uuid(trunc=32):
    """Returns a unique identifier in hex.
    
    Can be optionally truncated to a shorter string via the argument :trunc:. The result should still be properly
    random. """  # I think
    return uuid_.uuid4().hex[:trunc]


def uuid2(len=8, digits=True, lowercase=True, uppercase=False, hexdigits=False):
    """Returns a random :len: length string comprising of any combination of :digits:, :lowercase: letters, :uppercase:
    letters, or :hexdigits:.

    Note that the result need not be cryptographically random.
    """

    if not (digits or lowercase or uppercase or hexdigits):
        raise ValueError("At least one of the 'digits', 'lowercase', 'uppercase', 'hexdigits' arguments must be True.")
    valid_elements = set()
    if digits:
        valid_elements.update(string.digits)
    if lowercase:
        valid_elements.update(string.ascii_lowercase)
    if uppercase:
        valid_elements.update(string.ascii_uppercase)
    if hexdigits:
        valid_elements.update(string.hexdigits)
    valid_elements = list(valid_elements)

    return ''.join(random.choice(valid_elements) for _ in range(len))


def safe_issubclass(cls, classinfo):
    """As the builtin issubclass, but returns False instead of a TypeError if the first argument is not a class."""
    try:
        return issubclass(cls, classinfo)
    except TypeError:  # cls is not actually a class
        return False

    
def random_function(*args):
    """Picks one of its arguments uniformly at random, calls it, and returns the result.
    
    Example usage:
    >>> random_function(lambda: numpy.uniform(-2, -1), lambda: numpy.uniform(1, 2))
    """
    
    choice = random.randint(0, len(args) - 1)
    return args[choice]()
    

# https://stackoverflow.com/questions/37792112/python-file-of-the-caller
def file_loc():
    """Returns the directory of whatever file this function is called in.

    Example: calling file_loc() in the file located at /home/example_user/example_file.py will return the string
    '/home/example_user/example_file.py'
    """
    return os.path.dirname(inspect.stack()[1][1])


def assert_equal(o1, o2, getter=lambda x: x, error_msg='{o1} and {o2} are not equal'):
    """Checks that :getter(o1): and :getter(o2): are equal, and raises ValueError(:error_msg:) if they are not."""

    if getter(o1) == getter(o2):
        return
    else:
        raise ValueError(error_msg.format(o1=o1, o2=o2))


class AddBase:
    """Always returns the other object when added to. Example usage:

    >>> returnval = tools.AddBase()
    >>> for thing in things:
    ...     returnval += a_function(thing)
    """

    def __add__(self, other):
        return other

    def __radd__(self, other):
        return other


class ContainsAll:
    """Instances of this class always returns true when testing if something is contained in it."""
    def __contains__(self, item):
        return True


class DefaultException(Exception):
    """Exceptions with a default error message."""

    def __init__(self, msg=None):
        if msg is None:
            msg = self.default_msg
        super(DefaultException, self).__init__(msg)

    # Subclasses should provide the default_msg class or instance attribute.
