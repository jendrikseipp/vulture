from vulture import Vulture


def test_import_as_alias():
    definitions = """\
class A(object):
    pass
class B(object):
    pass
def C():
    pass
D = 42
"""
    imports = """\
from any_module import A as AliasedA
import B as AliasedB, C as AliasedC
import D as AliasedD
"""
    uses = """\
AliasedA()
AliasedB()
AliasedC()
AliasedD()
"""
    v = Vulture(verbose=True)
    v.scan(definitions)
    assert v.defined_attrs == []
    assert v.defined_funcs == ['A', 'B', 'C']
    assert v.defined_vars == ['D']
    assert v.used_attrs == []
    assert v.used_vars == []
    assert v.unused_attrs == []
    assert v.unused_funcs == ['A', 'B', 'C']
    assert v.unused_vars == ['D']

    v = Vulture(verbose=True)
    v.scan(definitions + imports)
    assert v.defined_attrs == []
    assert v.defined_funcs == ['A', 'B', 'C']
    assert v.defined_vars == ['D']
    assert v.used_attrs == []
    assert v.used_vars == []
    assert v.unused_attrs == []
    # Ignore unused imports. They are detected by pyflakes.
    assert v.unused_funcs == []
    assert v.unused_vars == []

    v = Vulture(verbose=True)
    v.scan(definitions + imports + uses)
    assert v.defined_attrs == []
    assert v.defined_funcs == ['A', 'B', 'C']
    assert v.defined_vars == ['D']
    assert v.used_attrs == []
    assert v.used_vars == ['AliasedA', 'AliasedB', 'AliasedC', 'AliasedD']
    assert v.unused_attrs == []
    assert v.unused_funcs == []
    assert v.unused_vars == []
