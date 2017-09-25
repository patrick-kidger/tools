import itertools
import math


__sentinel = object()
def rangeinf(start, stop=__sentinel, step=1):
    """Acts as range, however passing stop=math.inf will have it go forever."""
    # Allows us to pass just one argument and has it act as 'stop', with 'start' set to zero. This is the same
    # behaviour as the usual range function
    if stop == __sentinel:
        stop = start
        start = 0
    if stop is math.inf:
        return itertools.count(start, step)
    else:
        return range(start, stop, step)