import unittest

from src import deepattr


class TestAttrs(unittest.TestCase):
    def test_all(self):
        class A:
            pass

        class B:
            pass

        class C:
            y = [type('E', tuple(), {'z': [9]})]

        class D:
            x = [4, 5]

        sentinel = object()

        deepattr.deepsetattr(A, 'B', B)
        deepattr.deepsetattr(A, 'B.C', C)
        deepattr.deepsetattr(A, 'B.C.D', D)

        self.assertIs(deepattr.deepgetattr(A, 'B.C.D'), D)
        self.assertIs(deepattr.deepgetattr(A, 'B.C.D.asdf', sentinel), sentinel)
        self.assertEqual(deepattr.deepgetattr(A, 'B.C.D.x[0]'), 4)
        self.assertEqual(deepattr.deepgetattr(A.B, 'C.D.x[0]'), 4)
        self.assertEqual(deepattr.deepgetattr(A.B.C, 'D.x[0]'), 4)
        self.assertEqual(deepattr.deepgetattr(A, 'B.C.D.x[1]'), 5)
        self.assertEqual(deepattr.deepgetattr(A, 'B.C.y[0].z[0]'), 9)
        self.assertEqual(deepattr.deepgetattr(A.B.C, 'y[0].z[0]'), 9)
        self.assertEqual(deepattr.deepgetattr(A, 'B.C.y[0].z'), [9])

        self.assertEqual(deepattr.deephasattr(A, 'B.C'), True)
        self.assertEqual(deepattr.deephasattr(A, 'B.C.E'), False)

        deepattr.deepdelattr(A, 'B.C.D.x')
        deepattr.deepgetattr(A, 'B.C.D')
        with self.assertRaises(AttributeError):
            deepattr.deepgetattr(A, 'B.C.D.x')
        deepattr.deepdelattr(A, 'B.C.D')
        deepattr.deepgetattr(A, 'B.C')
        with self.assertRaises(AttributeError):
            deepattr.deepgetattr(A, 'B.C.D')
        deepattr.deepdelattr(A.B, 'C')
        with self.assertRaises(AttributeError):
            deepattr.deepgetattr(A.B, 'C')
