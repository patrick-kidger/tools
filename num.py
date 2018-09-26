import math


def clamp(val, min_, max_):
    """Clamps :val: to the range between :min_: and :max_:"""
    return min(max(val, min_), max_)


def round_mult(val, multiple, direction='round'):
    """Rounds :val: to the nearest :multiple:. The argument :direction: should be either 'round', 'up', or 'down'."""
    round_func = {'round': round, 'up': math.ceil, 'down': math.floor}
    return round_func[direction](val / multiple) * multiple


def num_digits(n):
    """Returns the number of digits in an integer :n:.

    Source:
    https://stackoverflow.com/a/2189827
    """

    if n > 0:
        return int(math.log10(n)) + 1
    elif n == 0:
        return 1
    else:
        return int(math.log10(-n)) + 2
