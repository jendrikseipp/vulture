import pytest

from vulture import core

from . import check


@pytest.fixture
def check_ignore():
    def examine(code, ignore_names, expected):
        v = core.Vulture(verbose=True, ignore_names=ignore_names)
        v.scan(code)
        check(v.get_unused_code(), expected)
    return examine


def test_var(check_ignore):
    code = """\
fio = 1
fao = 2
bar = 2
ftobar = 3
baz = 10000
funny = True
"""
    check_ignore(code, ['f?o*', 'ba[rz]'], ['funny'])


def test_function(check_ignore):
    code = """\
def foo_one():
    pass
def foo_two():
    pass
def foo():
    pass
def bar():
    pass
"""
    check_ignore(code, ['foo*'], ['bar'])


def test_class(check_ignore):
    code = """\
class Foo:
    def __init__(self):
        pass
"""
    check_ignore(code, ['Foo'], [])


def test_attribute(check_ignore):
    code = """\
class Foo:
    def __init__(self, attr_foo, attr_bar):
        self.attr_foo = attr_foo
        self.attr_bar = attr_bar
"""
    check_ignore(code, ['foo', '*_foo'], ['Foo', 'attr_bar'])
