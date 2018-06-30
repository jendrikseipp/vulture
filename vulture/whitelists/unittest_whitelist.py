from unittest import TestCase

TestCase.setUp
TestCase.tearDown
TestCase.setUpClass
TestCase.tearDownClass
TestCase.run
TestCase.skipTest
TestCase.debug
TestCase.failureException
TestCase.longMessage
TestCase.maxDiff
try:
    # new in Python 3.4
    TestCase.subTest
except AttributeError:
    pass

try:
    from unittest import mock
    # unittest.mock was introduced in Python 3.3
    mock.Mock.return_value
    mock.Mock.side_effect
except ImportError:
    pass
