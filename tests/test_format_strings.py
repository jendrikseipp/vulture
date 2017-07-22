import pytest
from vulture import Vulture

from . import check


@pytest.fixture
def v():
    return Vulture(verbose=True)


def test_old_format_string(v):
    v.scan("a = 1\n'%(a)s, %(b)d' % locals()")
    check(v.defined_funcs, [])
    check(v.defined_vars, ['a'])
    check(v.used_names, ['a', 'b', 'locals'])
    check(v.unused_vars, [])


def test_new_format_string(v):
    v.scan("a = 1\n'{a}, {b}'.format(**locals())")
    check(v.defined_funcs, [])
    check(v.defined_vars, ['a'])
    check(v.used_names, ['a', 'b', 'locals'])
    check(v.unused_vars, [])
