import pytest

import ast
from vulture import Vulture
from vulture.core import estimate_lines


@pytest.fixture
def wv():
    return Vulture(verbose=True, sort_by_size=True)


def test_size_function(wv):
    wv.scan("""\
def func():
    if "foo" == "bar":
        return "xyz"
    import sys
    return len(sys.argv)
""")
    assert wv.defined_funcs[0].size == 5


def test_size_class(wv):
    wv.scan("""\
class Foo(object):
    def bar():
        pass

    @staticmethod
    def func():
        if "foo" == "bar":
            return "xyz"
        import sys
        return len(sys.argv)
""")
    assert wv.defined_classes[0].size == 9

def test_estimate_lines():
    example = """
def identity(o):
    return o

@identity
class Foo(object):
    @identity
    @identity
    def bar(self):
        if "a" == "b":
            pass
        elif "b" == "c":
            pass
        else:
            pass
        with open("/dev/null") as f:
            f.write("")
        import sys
        while "b" > "a":
            pass
        else:
            pass
        for arg in sys.argv:
            if arg == "foo":
                break
        else:
            pass
        try:
            x = sys.argv[99]
        except IndexError:
            pass
        except Exception:
            pass
        else:
            pass
        try:
            1/0
        finally:
            return 99
"""
    node = ast.parse(example)
    # TODO improve estimate_lines to count the "else" clauses
    # and the estimate will get better (higher).
    assert estimate_lines(node) == 33
