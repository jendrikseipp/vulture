import ast
import sys

import pytest
from vulture import utils

from . import check_unreachable
from . import v
assert v  # Silence pyflakes


def check_condition(code, result):
    condition = ast.parse(code, mode='eval')
    assert utils._evaluate_condition(condition) == result


def test_false():
    check_condition('False', False)
    check_condition('None', False)
    check_condition("0", False)
    if sys.version_info > (3, 0):
        check_condition("1 - 1", False)


def test_empty():
    check_condition("''", False)
    check_condition("[]", False)
    check_condition("{}", False)


def test_true():
    check_condition("True", True)
    check_condition("2", True)
    check_condition("['foo', 'bar']", True)
    check_condition("{'a': 1, 'b': 2}", True)


def test_errors():
    conditions = [
        'foo',
        'foo and False',
        '__name__ == "__main__"',
        'False and 1',
        'False and foo',
        'chr(-1)',
        'getattr(True, "foo")',
        'hasattr(str, "foo")',
        'isinstance(True, True)',
        'not False']
    for condition in conditions:
        with pytest.raises(ValueError) as e:
            check_condition(condition, False)
        assert e.match("Condition cannot be evaluated")


def test_while(v):
    v.scan("""\
while False:
    pass
""")
    check_unreachable(v, 1, 2, 'while')


def test_while_nested(v):
    v.scan("""\
while True:
    while False:
        pass
""")
    check_unreachable(v, 2, 2, 'while')


def test_if_false(v):
    v.scan("""\
if False:
    pass
""")
    check_unreachable(v, 1, 2, 'if')


def test_elif_false(v):
    v.scan("""\
if bar():
    pass
elif False:
    print("Unreachable")
""")
    check_unreachable(v, 3, 2, 'if')


def test_nested_if_statements_false(v):
    v.scan("""\
if foo():
    if bar():
        pass
    elif False:
        print("Unreachable")
        pass
    elif something():
        print("Reachable")
    else:
        pass
else:
    pass
""")
    check_unreachable(v, 4, 3, 'if')


def test_if_false_same_line(v):
    v.scan("""\
if False: a = 1
else: c = 3
""")
    check_unreachable(v, 1, 1, 'if')


def test_if_true(v):
    v.scan("""\
if True:
    a = 1
    b = 2
else:
    c = 3
    d = 3
""")
    # For simplicity, we don't report the "else" line as dead code.
    check_unreachable(v, 5, 2, 'else')


def test_if_true_same_line(v):
    v.scan("""\
if True:
    a = 1
    b = 2
else: c = 3
d = 3
""")
    check_unreachable(v, 4, 1, 'else')


def test_nested_if_statements_true(v):
    v.scan("""\
if foo():
    if bar():
        pass
    elif True:
        if something():
            pass
        else:
            pass
    elif something_else():
        print("foo")
    else:
        print("bar")
else:
    pass
""")
    check_unreachable(v, 9, 4, 'else')
