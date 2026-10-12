import pathlib

import pytest

from . import check, v

assert v  # silence pyflakes


@pytest.fixture
def check_whitelist(v):
    def examine(code, results_before, results_after):
        v.scan(code)
        check(v.get_unused_code(), results_before)
        for item in v.get_unused_code():
            v.scan(item.get_whitelist_string())
        check(v.get_unused_code(), results_after)

    return examine


def test_unused_function(check_whitelist):
    code = """\
def func():
    pass
"""
    check_whitelist(code, ["func"], [])


def test_unused_class(check_whitelist):
    code = """\
class Foo:
    def __init__(self):
        pass
"""
    check_whitelist(code, ["Foo"], [])


def test_unused_variables(check_whitelist):
    code = """\
foo = 'unused'
bar = 'variable'
"""
    check_whitelist(code, ["foo", "bar"], [])


def test_unused_import(check_whitelist):
    code = """\
import xyz
import foo as bar
from abc import iou
from lorem import ipsum as dolor
"""
    check_whitelist(code, ["xyz", "bar", "iou", "dolor"], [])


def test_unused_attribute(check_whitelist):
    code = """\
class Foo:
    def bar(self):
        self.foobar = 'unused attr'
"""
    check_whitelist(code, ["Foo", "bar", "foobar"], [])


def test_unused_property(check_whitelist):
    code = """\
class Foo:
    @property
    def bar(self):
        pass
"""
    check_whitelist(code, ["Foo", "bar"], [])


def test_unreachable_code(check_whitelist):
    code = """\
def foo():
    return "Foo Bar"
    print("Hello")
"""
    check_whitelist(code, ["foo", "return"], ["return"])


def test_whitelist_entry_only_matches_its_own_location(v):
    """A generated entry must not silence same-named items elsewhere."""
    code = """\
def zeta_reservoir():
    pass
"""
    v.scan(code, filename="a.py")
    v.scan(code, filename="b.py")
    check(v.unused_funcs, ["zeta_reservoir", "zeta_reservoir"])

    v.scan("zeta_reservoir  # unused function (a.py:1)")

    check(v.unused_funcs, ["zeta_reservoir"])
    assert v.unused_funcs[0].filename == pathlib.Path("b.py")


def test_whitelist_entry_matches_its_own_location(v):
    v.scan(
        """\
def zeta_reservoir():
    pass
""",
        filename="a.py",
    )
    check(v.unused_funcs, ["zeta_reservoir"])

    v.scan("zeta_reservoir  # unused function (a.py:1)")

    check(v.unused_funcs, [])


def test_whitelist_entry_for_method(v):
    """Methods are prefixed with "_." in generated whitelists."""
    code = """\
class Foo:
    def bar(self):
        pass
"""
    v.scan(code, filename="a.py")
    v.scan(code, filename="b.py")
    check(v.unused_methods, ["bar", "bar"])

    v.scan("_.bar  # unused method (a.py:2)")

    check(v.unused_methods, ["bar"])
    assert v.unused_methods[0].filename == pathlib.Path("b.py")


def test_whitelist_entry_without_location(v):
    """A hand-written entry without a location keeps its old behaviour."""
    code = """\
def zeta_reservoir():
    pass
"""
    v.scan(code, filename="a.py")
    v.scan(code, filename="b.py")
    check(v.unused_funcs, ["zeta_reservoir", "zeta_reservoir"])

    v.scan("zeta_reservoir")

    check(v.unused_funcs, [])
