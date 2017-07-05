import pytest

from vulture import Vulture


@pytest.fixture
def wv():
    return Vulture(verbose=True, weigh=True)


def test_weigh_function(wv):
    wv.scan("""\
def func():
    if "foo" == "bar":
        return "xyz"
    import sys
    return len(sys.argv)
""")
    assert wv.defined_funcs[0].weight == 5


def test_weigh_class(wv):
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
    assert wv.defined_classes[0].weight == 8
