from vulture import Vulture

from . import skip_if_python_2
from . import skip_if_python_3


def check_min_confidence(code, min_conf, linenos, confidences):
    v = Vulture(verbose=True, min_confidence=min_conf)
    v.scan(code)
    for i, unused_item in enumerate(v.get_unused_code()):
        assert unused_item.lineno == linenos[i]
        assert unused_item.confidence == confidences[i]


def test_confidence_import():
    code = """\
import foo
"""
    check_min_confidence(code, 50, [1], [90])


def test_confidence_unreachable():
    code = """\
def foo():
    return
    bar()

foo()
"""
    check_min_confidence(code, 50, [3], [100])
    check_min_confidence(code, 100, [3], [100])


@skip_if_python_3
def test_function_arg_py2():
    code = """\
def foo(a):
    b = 3

foo(5)
"""
    check_min_confidence(code, 100, [], [])
    check_min_confidence(code, 60, [1, 2], [60, 60])
    check_min_confidence(code, 50, [1, 2], [60, 60])


@skip_if_python_2
def test_function_arg_py3():
    code = """\
def foo(a):
    b = 3

foo(5)
"""
    check_min_confidence(code, 100, [1], [100])
    check_min_confidence(code, 60, [1, 2], [100, 60])


def test_confidence_class():
    code = """\
class Foo:
    pass
"""
    check_min_confidence(code, 50, [1], [60])


def test_confidence_attr():
    code = """\
class Foo:
    self.b = 'something'

Foo()
"""
    check_min_confidence(code, 50, [2], [60])


def test_confidence_props():
    code = """\
class Foo:
    @property
    def some_prop():
        pass

Foo()
"""
    check_min_confidence(code, 50, [2], [60])
    check_min_confidence(code, 100, [], [])
