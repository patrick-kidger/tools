import random
import uuid as uuid_


def uuid(trunc=32):
    """Returns a unique identifier in hex.
    
    Can be optionally truncated to a shorter string via the argument :trunc:. Note that
    truncating a UUID in this way might not be what you want, though.
    """
    return uuid_.uuid4().hex[:trunc]

    
def random_function(*args):
    """Picks one of its arguments uniformly at random, calls it, and returns the result.
    
    Example usage:
    >>> random_function(lambda: numpy.uniform(-2, -1), lambda: numpy.uniform(1, 2))
    """
    
    choice = random.randint(0, len(args) - 1)
    return args[choice]()


class AddBase:
    """Always returns the other object when added to. Example usage:

    >>> returnval = tools.AddBase()
    >>> for thing in things:
    ...     returnval += a_function(thing)
    """

    def __add__(self, other):
        return other
