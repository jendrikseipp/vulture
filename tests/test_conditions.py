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
    conditions = ['foo',
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
    print(v.unreachable_code[0])
    check_unreachable(v, 1, 2, 'if-False')


def test_elif_false(v):
    v.scan("""\
if bar():
    pass
elif False:
    print("Unreachable")
""")
    print(v.unreachable_code[0])
    check_unreachable(v, 3, 2, 'if-False')


def test_nested_if_statements_false(v):
    v.scan("""\
if foo():
    if bar():
        pass
    elif False:
        print("Unreachable")
    elif something():
        print("Reachable")
    else:
        pass
else:
    pass
""")
    print(v.unreachable_code[0].size)
    check_unreachable(v, 4, 2, 'if-False')


def test_nested_if_statements_true(v):
    v.scan("""\
if foo():
    if bar():
        pass
    elif True:
        print("Reachable code starts")
        if something():
            pass
        else:
            print("Reachable code ends")
    elif something_else():
        print("I am unreachable")
    else:
        print("Unreachable")
        print("Else Block")
else:
    pass
""")
    print(v.unreachable_code[0].lineno)
    print(v.unreachable_code[0].size)
    check_unreachable(v, 10, 5, 'if-True')
