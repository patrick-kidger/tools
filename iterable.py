import itertools
import math


def rangeinf(start, stop=None, step=1):
    """Acts as range, however passing stop=math.inf or np.inf will have it go forever."""
    # Allows us to pass just one argument and has it act as 'stop', with 'start' set to zero. This is the same
    # behaviour as the usual range function
    if stop is None:
        stop = start
        start = 0
    if stop == math.inf:  # Also True for numpy.inf
        return itertools.count(start, step)
    else:
        return range(start, stop, step)


def single_true(iterable):
    """Checks that precisely one element of the iterable is truthy."""
    i = iter(iterable)
    return any(i) and not any(i)


def slice_pieces(sliceable, length):
    """Cuts a sliceable object into pieces of length 'length', and yields them one at a time."""
    if not sliceable:
        yield sliceable
    while sliceable:
        piece, sliceable = sliceable[:length], sliceable[length:]
        yield piece
