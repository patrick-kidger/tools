import unittest

from src import context


class A(context.WithAdder):
    def __init__(self, tape):
        self.tape = tape

    def __enter__(self):
        self.tape.append(0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tape.append(6)


class B(context.WithAdder):
    def __init__(self, tape):
        self.tape = tape

    def __enter__(self):
        self.tape.append(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tape.append(5)


class C(context.WithAdder):
    def __init__(self, tape):
        self.tape = tape

    def __enter__(self):
        self.tape.append(2)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tape.append(4)


class A2(context.WithAdder):
    def __init__(self, tape):
        self.tape = tape

    def __enter__(self):
        self.tape.append(0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tape.append(6)


class B2(context.WithAdder):
    def __init__(self, tape):
        self.tape = tape

    def __enter__(self):
        self.tape.append(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tape.append(5)


class C2(context.WithAdder):
    def __init__(self, tape):
        self.tape = tape

    def __enter__(self):
        self.tape.append(2)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tape.append(4)


class TestWithNothing(unittest.TestCase):
    def test_with_nothing(self):
        with context.WithNothing():
            pass


class TestWithAdder(unittest.TestCase):
    def test_with_adder(self):
        tape = []

        with A(tape) + B(tape) + C(tape):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])

    def test_with_adder2(self):
        tape = []

        with A(tape) + (B(tape) + C(tape)):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])

    def test_with_adder3(self):
        tape = []

        with (A(tape) + B(tape)) + C(tape):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])

    def test_with_adder4(self):
        tape = []

        with A(tape) + (B(tape) + C2(tape)):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])

    def test_with_adder5(self):
        tape = []

        with A(tape) + (B2(tape) + C(tape)):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])

    def test_with_adder6(self):
        tape = []

        with (A2(tape) + B(tape)) + C(tape):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])

    def test_with_adder7(self):
        tape = []

        with (A(tape) + B2(tape)) + C(tape):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])

    def test_with_adder8(self):
        tape = []

        with A2(tape) + (B(tape) + C2(tape)):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])

    def test_with_adder9(self):
        tape = []

        with A2(tape) + (B2(tape) + C(tape)):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])

    def test_with_adder10(self):
        tape = []

        with (A2(tape) + B(tape)) + C2(tape):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])

    def test_with_adder11(self):
        tape = []

        with (A(tape) + B2(tape)) + C2(tape):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])


class TestMultiWith(unittest.TestCase):
    def test_multi_with(self):
        tape = []

        with context.MultiWith([A(tape), B(tape), C(tape)]):
            tape.append(3)

        self.assertEqual(tape, [0, 1, 2, 3, 4, 5, 6])


class TestSetContextVariables(unittest.TestCase):
    def test_set_context(self):
        x = type('X', (), {})
        x.attr = True
        x.attr2 = True
        x.attr3 = True

        def callback():
            x.attr3 = False
        with context.set_context_variables(x, ['attr', 'attr2'], value=False, callback=callback):
            self.assertEqual(x.attr, False)
            self.assertEqual(x.attr2, False)
            self.assertEqual(x.attr3, True)
        self.assertEqual(x.attr, True)
        self.assertEqual(x.attr2, True)
        self.assertEqual(x.attr3, False)
