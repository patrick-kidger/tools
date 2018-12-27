import os
import time
import unittest

from src import misc


class TestUuid(unittest.TestCase):
    def test_basic_1(self):
        self.assertEqual(len(misc.uuid()), 32)
        for i in range(32):
            self.assertEqual(len(misc.uuid(i)), i)

    def test_basic_2(self):
        self.assertEqual(len(misc.uuid2()), 8)
        for i in range(32):
            self.assertEqual(len(misc.uuid2(i)), i)


class TestSafeSubclass(unittest.TestCase):
    def test_basic(self):
        class A:
            pass

        class B(A):
            pass
        self.assertEqual(misc.safe_issubclass(B, A), True)
        self.assertEqual(misc.safe_issubclass(A, B), False)
        self.assertEqual(misc.safe_issubclass('hi', A), False)


class TestRandomFunction(unittest.TestCase):
    def test_basic(self):
        for _ in range(10):
            res = misc.random_function(lambda: 1, lambda: 2)
            self.assertIn(res, [1, 2])


class TestTimeFunc(unittest.TestCase):
    def test_basic(self):
        for i in [0.1, 0.2, 0.3, 0.4]:
            def test_fun():
                time.sleep(i)
            timed_fn = misc.time_func(test_fun)
            self.assertAlmostEqual(timed_fn(), i, delta=0.005)


class TestFileLoc(unittest.TestCase):
    def test_file_loc(self):
        file_loc = misc.file_loc()
        rest, test = os.path.split(file_loc)
        rest, tools = os.path.split(rest)
        self.assertEqual(tools, 'tools')
        self.assertEqual(test, 'test')


class TestAssertEqual(unittest.TestCase):
    def test_assert_equal(self):
        misc.assert_equal(1, 1)
        misc.assert_equal([1], [1], getter=lambda x: x[0])
        with self.assertRaises(ValueError):
            misc.assert_equal(1, 2)


class TestAddBase(unittest.TestCase):
    def test_basic(self):
        x = misc.AddBase()

        class A:
            pass
        for o in [1, 'hi', object(), A, A(), [], [3], (), {}, set(), frozenset()]:
            self.assertEqual(o, x + o)
            self.assertEqual(o, o + x)


class TestContainsAll(unittest.TestCase):
    def test_basic(self):
        x = misc.ContainsAll()

        class A:
            pass

        for o in [1, 'hi', object(), A, A(), [], [3], (), {}, set(), frozenset()]:
            self.assertIn(o, x)


class TestDefaultException(unittest.TestCase):
    def test_basic(self):
        class A(misc.DefaultException):
            default_msg = 'some string'

        with self.assertRaisesRegex(A, A.default_msg):
            raise A

        with self.assertRaisesRegex(A, A.default_msg):
            raise A()

        with self.assertRaisesRegex(A, 'hi'):
            raise A('hi')
