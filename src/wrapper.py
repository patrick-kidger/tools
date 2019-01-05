import time


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


def compose(*fns):
    """Composes the given functions: compose(f, g, h)(x) == f(g(h(x)))"""

    assert len(fns) > 0

    def composed(*args, **kwargs):
        fn = fns[-1]
        x = fn(*args, **kwargs)
        for fn in fns[-2::-1]:
            x = fn(x)
        return x
    return composed


class getitemfn:
    """Converts a function to operate via __getitem__ syntax rather than the normal one.

    Note that this is not a 'dictionary' in any reasonable way: it cannot have reasonable methods for keys, values,
    items, for example.

    Example:
    >>> def f(x):
    ...    return x ** 2
    >>> g = getitemfn(f)
    >>> g[4]
    16
    """
    def __init__(self, fn, **kwargs):
        self.fn = fn
        super(getitemfn, self).__init__(**kwargs)

    def __getitem__(self, item):
        return self.fn(item)
