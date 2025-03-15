from vulture import core

from . import check


def check_ignore(
    code, ignore_names, ignore_decorators, ignore_class_attrs, expected
):
    v = core.Vulture(
        verbose=True,
        ignore_names=ignore_names,
        ignore_decorators=ignore_decorators,
        ignore_class_attrs=ignore_class_attrs,
    )
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
    check_ignore(code, ["f?o*", "ba[rz]"], [], [], ["funny"])


def test_var_and_attrs():
    code = """\
class Foo1:
    foo1: str
    foo2: str = ""
    foo3 = None
    foo4, foo5 = None, None
class Foo2:
    foo6: str
    foo7: str = ""
    foo8 = None
    foo9, foo0 = None, None
funny = True
"""
    check_ignore(code, [], [], ["Foo*"], ["Foo1", "Foo2", "funny"])
    check_ignore(
        code,
        [],
        [],
        ["Foo1"],
        [
            "Foo1",
            "Foo2",
            "funny",
            "foo6",
            "foo7",
            "foo8",
            "foo9",
            "foo0",
        ],
    )


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
    check_ignore(code, ["foo*"], [], [], ["bar"])


def test_async_function():
    code = """\
async def foobar():
    pass
async def bar():
    pass
"""
    check_ignore(code, ["foo*"], [], [], ["bar"])


def test_class():
    code = """\
class Foo:
    def __init__(self):
        pass
"""
    check_ignore(code, ["Foo"], [], [], [])


def test_class_ignore():
    code = """\
@bar
class Foo:
    pass

class Bar:
    pass
"""
    check_ignore(code, [], [], [], ["Foo", "Bar"])


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
    check_ignore(code, ["Foo"], ["@property"], [], [])
    check_ignore(code, ["Foo"], [], [], ["some_property", "foo_bar"])


def test_attribute():
    code = """\
class Foo:
    def __init__(self, attr_foo, attr_bar):
        self._attr_foo = attr_foo
        self._attr_bar = attr_bar
"""
    check_ignore(code, ["foo", "*_foo"], [], [], ["Foo", "_attr_bar"])


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
    check_ignore(code, [], ["@decor", "*@f.foobar"], [], ["prop_one"])
    check_ignore(code, [], ["*decor", "@*f.foobar"], [], ["prop_one"])


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
    check_ignore(code, [], ["@app.route", "@a.b"], [], ["foo"])


def test_decorated_property():
    code = """\
@bar
@property
def foo():
    pass
"""
    check_ignore(code, [], ["@bar"], [], [])
    check_ignore(code, [], ["@baz"], [], ["foo"])
    check_ignore(code, [], ["@property"], [], [])


def test_decorated_property_reversed():
    code = """\
@property
@bar
def foo():
    pass
"""
    check_ignore(code, [], ["@bar"], [], [])
    check_ignore(code, [], ["@property"], [], [])
    check_ignore(code, [], ["@b*r"], [], [])
    check_ignore(code, [], ["@barfoo"], [], ["foo"])


def test_decorated_class():
    code = """\
@barfoo
@foo.bar('foo')
class Bar:
    def __init__(self):
        pass
"""
    check_ignore(code, [], [], [], ["Bar"])
    check_ignore(code, [], ["@bar*"], [], [])
