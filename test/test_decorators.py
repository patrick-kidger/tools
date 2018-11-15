import unittest

from src import decorators as dec


class TestWithDefaults(unittest.TestCase):
    defaults = staticmethod(dec.with_defaults({'a': 4, 'b': 'hello', 'c': 7}))

    def test_basic(self):
        @dec.with_defaults({'a': 4})
        def func(a):
            return a
        self.assertEqual(func(), 4)
        self.assertEqual(func(5), 5)

    def test_unused(self):
        @self.defaults
        def func(a):
            return a
        self.assertEqual(func(), 4)
        self.assertEqual(func(5), 5)

    def test_existing_default(self):
        @self.defaults
        def func(a, b=3):
            return a, b
        self.assertEqual(func(), (4, 3))
        self.assertEqual(func(a=2), (2, 3))

    def test_keyword_only_args(self):
        @self.defaults
        def func(a, *, c):
            return a, c
        self.assertEqual(func(), (4, 7))
        self.assertEqual(func(a=2), (2, 7))
        self.assertEqual(func(c='hi'), (4, 'hi'))

        @self.defaults
        def func(*, a, b, c):
            return a, b, c
        self.assertEqual(func(), (4, 'hello', 7))
        self.assertEqual(func(a=2), (2, 'hello', 7))
        self.assertEqual(func(c='hi'), (4, 'hello', 'hi'))

        @self.defaults
        def func(*, a, d):
            return a, d
        self.assertEqual(func(d=7), (4, 7))
        with self.assertRaises(TypeError):
            func()  # argument for d not passed

    def test_defaults_to_left_of_non_defaults(self):
        with self.assertRaises(ValueError):
            @self.defaults
            def func(a, z):
                return a, z

    def test_many(self):
        @dec.with_defaults({'a': 3, 'b': 4, 'c': 5, 'd': 6, 'e': 7, 'f': 8})
        def func(a, b, c=1, d=2, *, e, f, g='hi', h='hello'):
            return a, b, c, d, e, f, g, h
        self.assertEqual(func(), (3, 4, 1, 2, 7, 8, 'hi', 'hello'))
        self.assertEqual(func(a=1, d=5, h=None), (1, 4, 1, 5, 7, 8, 'hi', None))

    def test_multiple_decorators(self):
        @dec.with_defaults({'a': 3})
        @dec.with_defaults({'b': 2})
        def func(a, b):
            return a, b
        self.assertEqual(func(), (3, 2))

    def test_alias_default(self):
        @dec.with_defaults({'a': 3})
        def func(b=dec.AliasDefault('a')):
            return b
        self.assertEqual(func(), 3)

    def test_has_default(self):
        @dec.with_defaults({'a': 3, 'x': 2})
        def func(b=dec.AliasDefault('a'), x=dec.HasDefault):
            return b, x
        self.assertEqual(func(), (3, 2))

        @dec.with_defaults({'x': 1, 'y': 2})
        def func(x=dec.HasDefault, y=dec.HasDefault):
            return x, y
        self.assertEqual(func(), (1, 2))

        @dec.with_defaults({'x': 1})
        def func(x=dec.HasDefault, y=dec.HasDefault):
            return x, y
        self.assertEqual(func(), (1, dec.HasDefault))

        @dec.with_defaults({'x': 1})
        @dec.with_defaults({'y': 2})
        def func(x=dec.HasDefault, y=dec.HasDefault):
            return x, y
        self.assertEqual(func(), (1, 2))
