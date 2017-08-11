import ast

from vulture import core


def check_condition(code, unsatisfiable=True):
    condition = ast.parse(code, mode='eval')
    assert core.condition_is_unsatisfiable(condition) == unsatisfiable


def test_False():
    check_condition('False')


def test_None():
    check_condition('None')


def test_empty():
    check_condition("''")
    check_condition("[]")
    check_condition("{}")


def test_zero():
    check_condition("1-1")


def test_True():
    check_condition("True", unsatisfiable=False)
    check_condition("1", unsatisfiable=False)


def test_multiple_conditiions():
    check_condition("False and 1")


def test_errors():
    check_condition("foo", unsatisfiable=False)
    check_condition("foo and False", unsatisfiable=False)
    check_condition("locals()[foo]", unsatisfiable=False)
