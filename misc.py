import random
import time
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
