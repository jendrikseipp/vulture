import pytest

from vulture import core

from . import check


@pytest.fixture
def check_ignore():
    def examine(code, expected, ignore_names=[], ignore_decorators=[]):
        v = core.Vulture(
                verbose=True, ignore_names=ignore_names,
                ignore_decorators=ignore_decorators)
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
    check_ignore(code, ['funny'], ['f?o*', 'ba[rz]'])


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
    check_ignore(code, ['bar'], ['foo*'])


def test_class(check_ignore):
    code = """\
class Foo:
    def __init__(self):
        pass
"""
    check_ignore(code, [], ['Foo'])


def test_property(check_ignore):
    code = """\
class Foo:
    @property
    def some_property(self, a):
        return a

    @property
    def foo_bar(self):
        return 'bar'
"""
    check_ignore(code, ['some_property', 'foo_bar'], ['Foo'], ['property'])


def test_attribute(check_ignore):
    code = """\
class Foo:
    def __init__(self, attr_foo, attr_bar):
        self.attr_foo = attr_foo
        self.attr_bar = attr_bar
"""
    check_ignore(code, ['Foo', 'attr_bar'], ['foo', '*_foo'])


def test_decorated_functions(check_ignore):
    code = """\
def decor():
    return help

class FooBar:
    def foobar(self):
        return help

    @property
    def prop_one(self):
        pass

f = FooBar()

@decor()
def bar():
    pass

@f.foobar
def foo():
    pass

@f.foobar()
def barfoo():
    pass
"""
    check_ignore(code, ['prop_one'], [], ['decor', 'f.foobar'])
