from pathlib import Path

from . import v
from vulture.core import Item

assert v  # Silence pyflakes


def test_item_repr(v):
    v.scan(
        """\
import os

message = "foobar"

class Foo:
    def bar():
        pass
"""
    )
    for item in v.get_unused_code():
        assert repr(item) == f"{item.name!r}"


def test_item_attr(v):
    v.scan("foo.bar = 'bar'")
    assert len(v.unused_attrs) == 1
    a = v.unused_attrs[0]
    assert a.name == "bar"
    assert a.first_lineno == 1
    assert a.last_lineno == 1


def test_item_class(v):
    v.scan(
        """\
class Foo:
    pass
"""
    )
    assert len(v.unused_classes) == 1
    c = v.unused_classes[0]
    assert c.name == "Foo"
    assert c.first_lineno == 1
    assert c.last_lineno == 2


def test_item_function(v):
    v.scan(
        """\
def add(a, b):
    return a + b
"""
    )
    assert len(v.unused_funcs) == 1
    f = v.unused_funcs[0]
    assert f.name == "add"
    assert f.first_lineno == 1
    assert f.last_lineno == 2


def test_item_import(v):
    v.scan(
        """\
import bar
from foo import *
"""
    )
    assert len(v.unused_imports) == 1
    i = v.unused_imports[0]
    assert i.name == "bar"
    assert i.first_lineno == 1
    assert i.last_lineno == 1


def test_item_property(v):
    v.scan(
        """\
@awesomify
class Foo:
    @property
    @wifi(
        username='dog',
        password='cat',
    )
    def bar(self):
        pass
Foo()
"""
    )
    assert len(v.unused_props) == 1
    p = v.unused_props[0]
    assert p.name == "bar"
    assert p.first_lineno == 3
    assert p.last_lineno == 9


def test_item_variable(v):
    v.scan("v = 'Vulture'")
    assert len(v.unused_vars) == 1
    var = v.unused_vars[0]
    assert var.name == "v"
    assert var.first_lineno == 1
    assert var.last_lineno == 1


def test_item_types(v):
    v.scan(
        """\
import os

message = "foobar"

class Foo:
    def bar():
        pass
"""
    )
    for item in (unused_code := v.get_unused_code()):
        assert isinstance(item, Item)
        assert isinstance(item.filename, Path)
        assert all(
            isinstance(field, str)
            for field in (item.name, item.typ, item.message)
        )
        assert all(
            isinstance(field, int)
            for field in (item.first_lineno, item.last_lineno, item.confidence)
        )
    assert isinstance(unused_code, list)
