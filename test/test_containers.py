import unittest

from src import containers as con


class TestRecord(unittest.TestCase):
    def test_create(self):
        con.Record(a=1, b=2)

    def test_args(self):
        rec = con.Record('a', b=2, c='hi')
        rec.a = 2
        with self.assertRaises(AttributeError):
            rec.d = 4
        del rec.a
        del rec.b

    def test_vals(self):
        rec = con.Record('a', 'alpha', b=2, c='hi', d=3, e=object())
        self.assertEqual(rec.b, 2)
        self.assertEqual(rec.c, 'hi')
        self.assertEqual(rec.d, 3)
        self.assertNotEqual(rec.e, object())

    def test_spec(self):
        spec = con.Record.spec('a', 'b', 'c', d=3, e=5)
        rec = con.Record('a', 'b', c=4, d=3, e=7)
        rec2 = spec(c=4, e=7)
        self.assertEqual(rec, rec2)

    def test_class_repetition(self):
        rec = con.Record('a', 'b')
        rec2 = con.Record('a', b=3)
        rec3 = con.Record.spec('a', 'b')()
        self.assertEqual(type(rec), type(rec2))
        self.assertNotEqual(type(rec), type(rec3))
        self.assertNotEqual(type(rec), con.Record)
