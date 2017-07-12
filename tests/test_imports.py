import pytest

from vulture import Vulture


@pytest.fixture
def v():
    return Vulture(verbose=True)


def test_import_star(v):
    v.scan("""\
from a import *
from a.b import *
""")
    assert v.defined_imports == ['*', '*']
    assert v.unused_imports == []


def test_import_from_future(v):
    v.scan("""from __future__ import division""")
    assert v.defined_imports == []
    assert v.unused_imports == []


def test_attribute_access(v):
    v.scan("""\
# foo.py
class Foo:
    pass

# bar.py
from foo import Foo

# main.py
import bar
bar.Foo
""")
    assert v.defined_imports == ['Foo', 'bar']
    assert v.unused_imports == []


def test_nested_import(v):
    v.scan("""\
import os.path
os.path.expanduser("~")
""")
    assert v.defined_imports == ['os']
    assert v.used_vars == ['os']
    assert v.unused_funcs == []
    assert v.unused_imports == []
    assert v.unused_vars == []


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
from any_module import A
import B, C
import D
"""

aliased_imports = """\
from any_module import A as AliasA
import B as AliasB, C as AliasC
import D as AliasD
"""

uses = """\
A()
B()
C()
D()
"""

aliased_uses = """\
AliasA()
AliasB()
AliasC()
AliasD()
"""


def test_definitions(v):
    v.scan(definitions)
    assert v.defined_classes == ['A', 'B']
    assert v.defined_funcs == ['C']
    assert v.defined_imports == []
    assert v.defined_vars == ['D']
    assert v.used_vars == []
    assert v.unused_classes == ['A', 'B']
    assert v.unused_funcs == ['C']
    assert v.unused_imports == []
    assert v.unused_vars == ['D']


def test_use_original(v):
    v.scan(definitions + uses)
    assert v.defined_classes == ['A', 'B']
    assert v.defined_funcs == ['C']
    assert v.defined_imports == []
    assert v.defined_vars == ['D']
    assert v.used_vars == ['A', 'B', 'C', 'D']
    assert v.unused_funcs == []
    assert v.unused_classes == []
    assert v.unused_imports == []
    assert v.unused_vars == []


def test_import_original(v):
    v.scan(definitions + imports)
    assert v.defined_classes == ['A', 'B']
    assert v.defined_funcs == ['C']
    assert v.defined_imports == ['A', 'B', 'C', 'D']
    assert v.defined_vars == ['D']
    assert v.used_vars == []
    assert v.unused_classes == ['A', 'B']
    assert v.unused_funcs == ['C']
    assert v.unused_imports == ['A', 'B', 'C', 'D']
    assert v.unused_vars == ['D']


def test_import_original_use_original(v):
    v.scan(definitions + imports + uses)
    assert v.defined_classes == ['A', 'B']
    assert v.defined_funcs == ['C']
    assert v.defined_imports == ['A', 'B', 'C', 'D']
    assert v.defined_vars == ['D']
    assert v.used_vars == ['A', 'B', 'C', 'D']
    assert v.unused_classes == []
    assert v.unused_funcs == []
    assert v.unused_imports == []
    assert v.unused_vars == []


def test_import_original_use_alias(v):
    v.scan(definitions + imports + aliased_uses)
    assert v.defined_classes == ['A', 'B']
    assert v.defined_funcs == ['C']
    assert v.defined_imports == ['A', 'B', 'C', 'D']
    assert v.defined_vars == ['D']
    assert v.used_vars == ['AliasA', 'AliasB', 'AliasC', 'AliasD']
    assert v.unused_classes == ['A', 'B']
    assert v.unused_funcs == ['C']
    assert v.unused_imports == ['A', 'B', 'C', 'D']
    assert v.unused_vars == ['D']


def test_import_alias(v):
    v.scan(definitions + aliased_imports)
    assert v.defined_classes == ['A', 'B']
    assert v.defined_funcs == ['C']
    assert v.defined_imports == ['AliasA', 'AliasB', 'AliasC', 'AliasD']
    assert v.defined_vars == ['D']
    assert v.used_vars == []
    assert v.unused_classes == []
    assert v.unused_funcs == []
    assert v.unused_imports == ['AliasA', 'AliasB', 'AliasC', 'AliasD']
    assert v.unused_vars == []


def test_import_alias_use_original(v):
    v.scan(definitions + aliased_imports + uses)
    assert v.defined_classes == ['A', 'B']
    assert v.defined_funcs == ['C']
    assert v.defined_imports == ['AliasA', 'AliasB', 'AliasC', 'AliasD']
    assert v.defined_vars == ['D']
    assert v.used_vars == ['A', 'B', 'C', 'D']
    assert v.unused_classes == []
    assert v.unused_funcs == []
    assert v.unused_imports == ['AliasA', 'AliasB', 'AliasC', 'AliasD']
    assert v.unused_vars == []


def test_import_alias_use_alias(v):
    v.scan(definitions + aliased_imports + aliased_uses)
    assert v.defined_classes == ['A', 'B']
    assert v.defined_funcs == ['C']
    assert v.defined_imports == ['AliasA', 'AliasB', 'AliasC', 'AliasD']
    assert v.defined_vars == ['D']
    assert v.used_vars == ['AliasA', 'AliasB', 'AliasC', 'AliasD']
    assert v.unused_classes == []
    assert v.unused_funcs == []
    assert v.unused_imports == []
    assert v.unused_vars == []
