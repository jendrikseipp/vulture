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


def test_vars(check_ignore):
    code = """\
foo = 1
bar = 2
three = 3
funny = True
"""
    check_ignore(code, ['f*', 'bar'], ['three'])


def test_ignore_function(check_ignore):
    code = """\
def foo():
    pass
def foo_ignored():
    pass
"""
    check_ignore(code, ['foo_ignored'], ['foo'])


def test_function_glob(check_ignore):
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


def test_class_ignored(check_ignore):
    code = """\
class Foo:
    def __init__(self):
        pass
"""
    check_ignore(code, ['Foo'], [])


def test_property(check_ignore):
    code = """\
class Foo:
    @property
    def some_property(self, a):
        return a
"""
    check_ignore(code, ['Foo', 'property'], ['some_property'])


def test_attribute(check_ignore):
    code = """\
class Foo:
    def __init__(self, attr_foo, attr_bar):
        self.attr_foo = attr_foo
        self.attr_bar = attr_bar
"""
    check_ignore(code, ['*_foo'], ['Foo', 'attr_bar'])
