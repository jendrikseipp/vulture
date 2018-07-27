from vulture import core

from . import check, skip_if_not_has_async


def check_ignore(code, expected, ignore_names, ignore_decorators):
    v = core.Vulture(
            verbose=True, ignore_names=ignore_names,
            ignore_decorators=ignore_decorators)
    v.scan(code)
    check(v.get_unused_code(), expected)


def test_var():
    code = """\
fio = 1
fao = 2
bar = 2
ftobar = 3
baz = 10000
funny = True
"""
    check_ignore(code, ['funny'], ['f?o*', 'ba[rz]'], [])


def test_function():
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
    check_ignore(code, ['bar'], ['foo*'], [])


@skip_if_not_has_async
def test_async_function():
    code = """\
async def foobar():
    pass
async def bar():
    pass
"""
    check_ignore(code, ['bar'], ['foo*'], [])


def test_class():
    code = """\
class Foo:
    def __init__(self):
        pass
"""
    check_ignore(code, [], ['Foo'], [])


def test_property():
    code = """\
class Foo:
    @property
    def some_property(self, a):
        return a

    @property
    @bar
    def foo_bar(self):
        return 'bar'
"""
    check_ignore(code, [], ['Foo'], ['@property'])
    check_ignore(code, ['some_property', 'foo_bar'], ['Foo'], [])


def test_attribute():
    code = """\
class Foo:
    def __init__(self, attr_foo, attr_bar):
        self.attr_foo = attr_foo
        self.attr_bar = attr_bar
"""
    check_ignore(code, ['Foo', 'attr_bar'], ['foo', '*_foo'], [])


def test_decorated_functions():
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

@bar
@foo
@f.foobar()
def barfoo():
    pass
"""
    check_ignore(code, ['prop_one'], [], ['decor', 'f.foobar'])
    check_ignore(code, ['prop_one'], [], ['@decor', '@f.foobar'])


@skip_if_not_has_async
def test_decorated_async_functions():
    code = """\
@app.route('something')
@foobar
async def async_function():
    pass

@a.b.c
async def foo():
    pass
"""
    check_ignore(code, ['foo'], [], ['@app.route', '@a.b'])


def test_decorated_property():
    code = """\
@bar
@property
def foo():
    pass
"""
    check_ignore(code, [], [], ['@bar'])
    check_ignore(code, ['foo'], [], ['@baz'])
    check_ignore(code, [], [], ['property'])
    check_ignore(code, [], [], ['@property'])


def test_decorated_class():
    code = """\
@barfoo
@foo.bar('foo')
class Bar:
    def __init__(self):
        pass
"""
    check_ignore(code, ['Bar'], [], [])
    check_ignore(code, [], [], ['@bar*'])
