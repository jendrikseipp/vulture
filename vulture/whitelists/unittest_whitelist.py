import unittest

from whitelist_utils import Whitelist

unittest.TestCase.setUp
unittest.TestCase.tearDown
unittest.TestCase.setUpClass
unittest.TestCase.tearDownClass
unittest.TestCase.run
unittest.TestCase.skipTest
unittest.TestCase.debug
unittest.TestCase.failureException
unittest.TestCase.longMessage
unittest.TestCase.maxDiff
if hasattr(unittest.TestCase, 'subTest'):
    # new in Python 3.4
    unittest.TestCase.subTest

# unittest.mock
whitelist_mock = Whitelist()
whitelist_mock.return_value
whitelist_mock.side_effect
