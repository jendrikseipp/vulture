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
