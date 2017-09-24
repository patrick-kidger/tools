import itertools
import math


_sentinel = object()
def rangeinf(start, stop=_sentinel, step=1):
    """Acts as range, however passing stop=None will have it go forever."""
    # Allows us to pass just one argument and has it act as 'stop', with 'start' set to zero. This is the same
    # behaviour as the usual range function
    if stop == _sentinel:
        stop = start
        start = 0
    if stop is math.inf:
        return itertools.count(start, step)
    else:
        return range(start, stop, step)