from unittest import TestCase, mock

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

# unittest.mock
mock.Mock.return_value
mock.Mock.side_effect
