import ast
import pytest
import sys

from vulture import utils
from . import check_unreachable
from . import v
assert v  # Silence pyflakes


def check_condition(code, result):
    condition = ast.parse(code, mode='eval')
    assert utils.evaluate_condition(condition) == result


def test_false():
    check_condition('False', False)
    check_condition('None', False)
    check_condition("0", False)
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
    with pytest.raises(ValueError) as e:
        check_condition("foo", False)
        # checks NameError is handled properly
        check_condition("foo and False", False)
        check_condition('__name__ == "__main__"', False)
        # checks ValueError is handled properly
        check_condition("False and 1", False)
        check_condition("False and foo", False)
        check_condition('chr(-1)', False)
        # checks AttributeError is handled properly
        check_condition('getattr(True, "foo")', False)
        check_condition("hasattr(str, 'foo')", False)
        # checks TypeError is handled properly
        check_condition('isinstance(True, True)', False)

        check_condition("not False", False)

    assert e.match("Condition cannot be evaluated")


def test_while(v):
    v.scan("""\
def func():
    while False:
        pass
func()
""")
    check_unreachable(v, 2, 2, 'while')


def test_while_nested(v):
    v.scan("""\
def foo():
    while True:
        while False:
            pass
""")


def test_if_false(v):
    v.scan("""\
def foo():
    if False:
        pass
foo()
""")
    check_unreachable(v, 2, 2, 'if')


def test_elif_false(v):
    v.scan("""\
def foo():
    if bar():
        pass
    elif False:
        print("Unreachable")
foo()
""")
    check_unreachable(v, 4, 2, 'if')


def test_nested_if_statements_for_false(v):
    v.scan("""\
def foo():
    if foo():
        if bar():
            pass
        elif False:
            print("Unreachable")
        else:
            pass
    else:
        pass
""")
    check_unreachable(v, 5, 4, 'if')


def test_nested_if_statements_for_true(v):
    v.scan("""\
def foo():
    if foo():
        if bar():
            pass
        elif True:
            print("Unreachable")
        else:
            pass
    else:
        pass
""")
    check_unreachable(v, 5, 4, 'if')
