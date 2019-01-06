import collections as co
import re


def is_magic(item):
    """Whether or not the specified string is __magic__"""
    return item.startswith('__') and item.startswith('__')


def split(delimiters, string, maxsplit=0):
    """Splits a :string: on multiple :delimiters:.

    Source:
    https://stackoverflow.com/a/13184791
    """
    regex_pattern = '|'.join(map(re.escape, delimiters))
    return re.split(regex_pattern, string, maxsplit)


def find_nth(haystack, needle, n):
    """Finds the nth occurrence of a substring 'needle' in a larger string 'haystack'."""
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


def re_sub_recursive(pattern, sub, inputstr):
    """Recursive regex.

    :str pattern: The regex pattern
    :str sub: What to substitute the regex pattern for.
    :str inputstr: The string to perform the substitutions on."""
    patt = re.compile(pattern)

    old_inputstr = inputstr
    inputstr = patt.sub(sub, inputstr)
    while old_inputstr != inputstr:
        old_inputstr = inputstr
        inputstr = patt.sub(sub, inputstr)

    return inputstr


class UniqueString:
    """Used to make strings unique. For every string it is called on, it will keep a record of how many times that
    string has been supplied to it, and return it with an appropriate disambiguating number attached to it.
    """

    def __init__(self, format_string='{string}{index}'):
        """See UniqueString.__doc__.

        Arguments:
            format_string: Should be a string containing '{string}' and/or '{index}', which will specify the output
                format of the disambiguated string. Defaults to '{string}{index}'.
        """
        self.counter = co.defaultdict(lambda: 0)
        self.format_string = format_string

    def __call__(self, string):
        """See UniqueString.__doc__.

        Arguments:
            string: The string to be disambiguated.
        """
        index = self.counter[string]
        self.counter[string] += 1
        return self.format_string.format(string=string, index=index)

