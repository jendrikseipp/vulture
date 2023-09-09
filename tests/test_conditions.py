import ast

from vulture import utils

from . import v

assert v  # Silence pyflakes


def check_condition(code, result):
    condition = ast.parse(code, mode="eval").body
    if result:
        assert utils.condition_is_always_true(condition)
    else:
        assert utils.condition_is_always_false(condition)


def test_false():
    check_condition("False", False)
    check_condition("None", False)
    check_condition("0", False)


def test_empty():
    check_condition("''", False)
    check_condition("[]", False)
    check_condition("{}", False)


def test_true():
    check_condition("True", True)
    check_condition("2", True)
    check_condition("'s'", True)
    check_condition("['foo', 'bar']", True)
    check_condition("{'a': 1, 'b': 2}", True)


def test_complex_conditions():
    conditions = [
        ("foo and False", True, False),
        ("foo or False", False, False),
        ("foo and True", False, False),
        ("foo or True", False, True),
        ("False and foo", True, False),
        ("False and 1", True, False),
        ("not False", False, True),
        ("not True", True, False),
        ("not foo", False, False),
        ("foo and (False or [])", True, False),
        ('(foo and bar) or {"a": 1}', False, True),
    ]
    for condition, always_false, always_true in conditions:
        condition = ast.parse(condition, mode="eval").body
        assert not (always_false and always_true)
        assert utils.condition_is_always_false(condition) == always_false
        assert utils.condition_is_always_true(condition) == always_true


def test_errors():
    conditions = [
        "foo",
        '__name__ == "__main__"',
        "chr(-1)",
        'getattr(True, "foo")',
        'hasattr(str, "foo")',
        "isinstance(True, True)",
        "globals()",
        "locals()",
        "().__class__",
    ]
    for condition in conditions:
        condition = ast.parse(condition, mode="eval").body
        assert not utils.condition_is_always_false(condition)
        assert not utils.condition_is_always_true(condition)
