import ast

from vulture import utils
from . import check_unreachable
from . import v
assert v  # Silence pyflakes


def check_condition(code, unsatisfiable=True):
    condition = ast.parse(code, mode='eval')
    assert utils.condition_is_unsatisfiable(condition) == unsatisfiable


def test_false():
    check_condition('False')
    check_condition('None')
    check_condition("0")


def test_empty():
    check_condition("''")
    check_condition("[]")
    check_condition("{}")


def test_true():
    check_condition("True", unsatisfiable=False)
    check_condition("1", unsatisfiable=False)


def test_errors():
    check_condition("False and 1", unsatisfiable=False)
    check_condition("False and foo", unsatisfiable=False)
    check_condition("foo", False)
    check_condition("foo and False", False)
    check_condition('chr(-1)', False)
    check_condition('getattr(True, "foo")', False)
    check_condition('isinstance(True, True)', False)
    check_condition('__name__ == "__main__"', False)
    check_condition("hasattr(str, 'foo')", False)


def test_while(v):
    v.scan("""\
def func():
    while False:
        pass
func()
""")
    check_unreachable(v, 2, 2, 'while')
