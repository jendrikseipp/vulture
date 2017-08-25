import sys

from vulture import core
from . import skip_if_not_has_async

dc = core.DEFAULT_CONFIDENCE


def check_min_confidence(code, min_confidence, expected):
    v = core.Vulture(verbose=True)
    v.scan(code)
    detected = dict(
        (item.name, item.confidence)
        for item in v.get_unused_code(min_confidence=min_confidence))
    assert detected == expected


def test_confidence_import():
    code = """\
import foo
"""
    check_min_confidence(code, 50, {'foo': 90})
    check_min_confidence(code, 100, {})


def test_confidence_unreachable():
    code = """\
def foo():
    return
    bar()

foo()
"""
    check_min_confidence(code, 50, {'return': 100})
    check_min_confidence(code, 100, {'return': 100})


def test_function_arg():
    code = """\
def foo(a):
    b = 3

foo(5)
"""
    if sys.version_info < (3, 0):
        # Python 2
        check_min_confidence(code, 50, {'a': dc, 'b': dc})
        check_min_confidence(code, dc, {'a': dc, 'b': dc})
        check_min_confidence(code, 100, {})
    else:
        # Python 3
        check_min_confidence(code, 50, {'a': 100, 'b': dc})
        check_min_confidence(code, dc, {'a': 100, 'b': dc})
        check_min_confidence(code, 100, {'a': 100})


def test_confidence_class():
    code = """\
class Foo:
    pass
"""
    check_min_confidence(code, 50, {'Foo': dc})
    check_min_confidence(code, 100, {})


def test_confidence_attr():
    code = "A.b = 'something'"
    check_min_confidence(code, 50, {'b': dc})
    check_min_confidence(code, 100, {})


def test_confidence_props():
    code = """\
class Foo:
    @property
    def some_prop():
        pass

Foo()
"""
    check_min_confidence(code, 50, {'some_prop': dc})
    check_min_confidence(code, 100, {})


@skip_if_not_has_async
def test_confidence_async_def():
    code = """\
async def foo():
    if bar():
        pass
    else:
        print("Else")
"""
    check_min_confidence(code, 50, {'foo': dc})
    check_min_confidence(code, 75, {})
