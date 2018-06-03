import ast
import sys

from vulture import utils

from . import check_unreachable
from . import v
assert v  # Silence pyflakes


def check_condition(code, result):
    condition = ast.parse(code, mode='eval').body
    if result:
        assert utils.condition_is_always_true(condition)
    else:
        assert utils.condition_is_always_false(condition)


def test_false():
    check_condition('False', False)
    check_condition('None', False)
    check_condition("0", False)
    # Only Python 3.0-3.6 allows addition and subtraction in ast.literal_eval.
    # (see https://bugs.python.org/issue31778)
    if (3, 0) <= sys.version_info < (3, 7):
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


def test_complex_conditions():
    conditions = [
        ('foo and False', True, False),
        ('foo or False', False, False),
        ('foo and True', False, False),
        ('foo or True', False, True),
        ('False and foo', True, False),
        ('False and 1', True, False),
        ('not False', False, True),
        ('not True', True, False),
        ('not foo', False, False),
        ('foo and (False or [])', True, False),
        ('(foo and bar) or {"a": 1}', False, True),
    ]
    for condition, always_false, always_true in conditions:
        condition = ast.parse(condition, mode='eval').body
        assert not (always_false and always_true)
        assert utils.condition_is_always_false(condition) == always_false
        assert utils.condition_is_always_true(condition) == always_true


def test_errors():
    conditions = [
        'foo',
        '__name__ == "__main__"',
        'chr(-1)',
        'getattr(True, "foo")',
        'hasattr(str, "foo")',
        'isinstance(True, True)',
        'globals()',
        'locals()',
        '().__class__',
    ]
    for condition in conditions:
        condition = ast.parse(condition, mode='eval').body
        assert not utils.condition_is_always_false(condition)
        assert not utils.condition_is_always_true(condition)


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
