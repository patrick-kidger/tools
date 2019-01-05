import time
import unittest

from src import wrapper


class TestTimeFunc(unittest.TestCase):
    def test_basic(self):
        for i in [0.1, 0.2, 0.3, 0.4]:
            def test_fun():
                time.sleep(i)
            timed_fn = wrapper.time_func(test_fun)
            self.assertAlmostEqual(timed_fn(), i, delta=0.005)


class TestCompose(unittest.TestCase):
    def test_basic(self):
        x = []

        def f(i):
            x.append(i)

        def g(i):
            x.append(3)
            return 5

        def h(*args, **kwargs):
            x.append(args)
            x.append(kwargs)

        c = wrapper.compose(f, g, h)
        c(1, 2, hi='exa')
        self.assertEqual(x, [(1, 2), {'hi': 'exa'}, 3, 5])

        c(4, 5, exa='hi')
        self.assertEqual(x, [(1, 2), {'hi': 'exa'}, 3, 5, (4, 5), {'exa': 'hi'}, 3, 5])


class TestGetItemFn(unittest.TestCase):
    def test_basic(self):
        def f(x):
            return x ** 2

        g = wrapper.getitemfn(f)
        self.assertEqual(g[4], 16)
        self.assertEqual(g[3], 9)
