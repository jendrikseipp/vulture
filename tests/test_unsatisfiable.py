import ast

from .test_unreachable import check_unreachable
from vulture import utils
from . import v
assert v  # Silence pyflakes


def check_condition(code, unsatisfiable=True):
    condition = ast.parse(code, mode='eval')
    assert utils.condition_is_unsatisfiable(condition) == unsatisfiable


def test_false():
    check_condition('False')


def test_none():
    check_condition('None')


def test_empty():
    check_condition("''")
    check_condition("[]")
    check_condition("{}")


def test_zero():
    check_condition("1 - 1")
    check_condition("0")


def test_true():
    check_condition("True", unsatisfiable=False)
    check_condition("1", unsatisfiable=False)


def test_multiple_conditions():
    check_condition("False and 1")
    check_condition("False and foo")  # should not raise ValueError


def test_hasattr():
    check_condition("hasattr(str, 'foo')")


def test_errors():
    check_condition("foo", unsatisfiable=False)  # raises NameError
    check_condition("foo and False", unsatisfiable=False)  # raises NameError
    check_condition('chr(-1)', unsatisfiable=False)  # raises ValueError
    check_condition('getattr(True, "foo")', False)  # raises AttributeError
    check_condition('isinstance(True, True)', False)  # raises TypeError


def test_while(v):
    v.scan("""\
def func():
    while False:
        pass
func()
""")
    check_unreachable(v, 2, 1, 'while')
