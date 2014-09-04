import pytest

from vulture import Vulture


@pytest.fixture
def v():
    return Vulture(verbose=True)


def test_old_format_string(v):
    v.scan("a = 1\n'%(a)s, %(b)d' % locals()")
    assert v.defined_funcs == []
    assert v.defined_vars == ['a']
    assert v.used_vars == ['a', 'b', 'locals']
    assert v.unused_vars == []


def test_new_format_string(v):
    v.scan("a = 1\n'{a}, {b}'.format(**locals())")
    assert v.defined_funcs == []
    assert v.defined_vars == ['a']
    assert v.used_vars == ['a', 'b', 'locals']
    assert v.unused_vars == []
