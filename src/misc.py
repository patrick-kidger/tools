import random
import string
import time
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

    if digits and lowercase and uppercase and hexdigits is False:
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
    
    
def time_func(func):
    """Times how long a function takes to run.
    
    It doesn't do anything clever to avoid the various pitfalls of timing a function's runtime.
    (Interestingly, the timeit module doesn't supply a straightforward interface to run a particular
    function.)
    """
    
    def timed(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        return end - start
    return timed


class AddBase:
    """Always returns the other object when added to. Example usage:

    >>> returnval = tools.AddBase()
    >>> for thing in things:
    ...     returnval += a_function(thing)
    """

    def __add__(self, other):
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
