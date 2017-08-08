from vulture import core

from . import skip_if_python_2
from . import skip_if_python_3

dc = core.DEFAULT_CONFIDENCE


def check_min_confidence(code, min_conf, tests):
    v = core.Vulture(verbose=True, min_confidence=min_conf)
    v.scan(code)
    for item, (lineno, confidence) in zip(v.get_unused_code(), tests):
        assert item.lineno == lineno
        assert item.confidence == confidence


def test_confidence_import():
    code = """\
import foo
"""
    check_min_confidence(code, 50, [(1, 90)])


def test_confidence_unreachable():
    code = """\
def foo():
    return
    bar()

foo()
"""
    check_min_confidence(code, 50, [(3, 100)])
    check_min_confidence(code, 100, [(3, 100)])


@skip_if_python_3
def test_function_arg_py2():
    code = """\
def foo(a):
    b = 3

foo(5)
"""
    check_min_confidence(code, 100, [])
    check_min_confidence(code, dc, [(1, dc), (2, dc)])
    check_min_confidence(code, 50, [(1, dc), (2, dc)])


@skip_if_python_2
def test_function_arg_py3():
    code = """\
def foo(a):
    b = 3

foo(5)
"""
    check_min_confidence(code, 100, [(1, 100)])
    check_min_confidence(code, dc, [(1, 100), (2, dc)])


def test_confidence_class():
    code = """\
class Foo:
    pass
"""
    check_min_confidence(code, 50, [(1, dc)])


def test_confidence_attr():
    code = """\
class Foo:
    self.b = 'something'

Foo()
"""
    check_min_confidence(code, 50, [(2, dc)])


def test_confidence_props():
    code = """\
class Foo:
    @property
    def some_prop():
        pass

Foo()
"""
    check_min_confidence(code, 50, [(2, dc)])
    check_min_confidence(code, 100, [])
