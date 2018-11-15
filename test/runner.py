import unittest

from . import test_containers
from . import test_decorators
from . import test_deepattr


loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(test_containers))
suite.addTests(loader.loadTestsFromModule(test_decorators))
suite.addTests(loader.loadTestsFromModule(test_deepattr))

runner = unittest.TextTestRunner()
result = runner.run(suite)
