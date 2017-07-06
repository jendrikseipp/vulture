import pytest

from vulture import Vulture


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

    def func():
        if "foo" == "bar":
            return "xyz"
        import sys
        return len(sys.argv)
""")
    assert wv.defined_classes[0].size == 8
