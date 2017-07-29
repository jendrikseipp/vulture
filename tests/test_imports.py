from . import check, v
assert v  # Silence pyflakes.


def test_import_star(v):
    v.scan("""\
from a import *
from a.b import *
""")
    check(v.defined_imports, [])
    check(v.unused_imports, [])


def test_import_from_future(v):
    v.scan("""from __future__ import division""")
    check(v.defined_imports, [])
    check(v.unused_imports, [])


def test_double_import(v):
    v.scan("""\
import foo as bar
import foo
""")
    check(v.defined_imports, ['bar', 'foo'])
    # Once the bar import is removed, the foo import will be detected.
    check(v.unused_imports, ['bar'])


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
    check(v.defined_imports, ['Foo', 'bar'])
    check(v.unused_imports, [])


def test_nested_import(v):
    v.scan("""\
import os.path
os.path.expanduser("~")
""")
    check(v.defined_imports, ['os'])
    check(v.used_names, ['os'])
    check(v.unused_funcs, [])
    check(v.unused_imports, [])
    check(v.unused_vars, [])


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
    check(v.defined_classes, ['A', 'B'])
    check(v.defined_funcs, ['C'])
    check(v.defined_imports, [])
    check(v.defined_vars, ['D'])
    check(v.used_names, [])
    check(v.unused_classes, ['A', 'B'])
    check(v.unused_funcs, ['C'])
    check(v.unused_imports, [])
    check(v.unused_vars, ['D'])


def test_use_original(v):
    v.scan(definitions + uses)
    check(v.defined_classes, ['A', 'B'])
    check(v.defined_funcs, ['C'])
    check(v.defined_imports, [])
    check(v.defined_vars, ['D'])
    check(v.used_names, ['A', 'B', 'C', 'D'])
    check(v.unused_funcs, [])
    check(v.unused_classes, [])
    check(v.unused_imports, [])
    check(v.unused_vars, [])


def test_import_original(v):
    v.scan(definitions + imports)
    check(v.defined_classes, ['A', 'B'])
    check(v.defined_funcs, ['C'])
    check(v.defined_imports, ['A', 'B', 'C', 'D'])
    check(v.defined_vars, ['D'])
    check(v.used_names, [])
    check(v.unused_classes, ['A', 'B'])
    check(v.unused_funcs, ['C'])
    check(v.unused_imports, ['A', 'B', 'C', 'D'])
    check(v.unused_vars, ['D'])


def test_import_original_use_original(v):
    v.scan(definitions + imports + uses)
    check(v.defined_classes, ['A', 'B'])
    check(v.defined_funcs, ['C'])
    check(v.defined_imports, ['A', 'B', 'C', 'D'])
    check(v.defined_vars, ['D'])
    check(v.used_names, ['A', 'B', 'C', 'D'])
    check(v.unused_classes, [])
    check(v.unused_funcs, [])
    check(v.unused_imports, [])
    check(v.unused_vars, [])


def test_import_original_use_alias(v):
    v.scan(definitions + imports + aliased_uses)
    check(v.defined_classes, ['A', 'B'])
    check(v.defined_funcs, ['C'])
    check(v.defined_imports, ['A', 'B', 'C', 'D'])
    check(v.defined_vars, ['D'])
    check(v.used_names, ['AliasA', 'AliasB', 'AliasC', 'AliasD'])
    check(v.unused_classes, ['A', 'B'])
    check(v.unused_funcs, ['C'])
    check(v.unused_imports, ['A', 'B', 'C', 'D'])
    check(v.unused_vars, ['D'])


def test_import_alias(v):
    v.scan(definitions + aliased_imports)
    check(v.defined_classes, ['A', 'B'])
    check(v.defined_funcs, ['C'])
    check(v.defined_imports, ['AliasA', 'AliasB', 'AliasC', 'AliasD'])
    check(v.defined_vars, ['D'])
    check(v.used_names, ['A', 'B', 'C', 'D'])
    check(v.unused_classes, [])
    check(v.unused_funcs, [])
    check(v.unused_imports, ['AliasA', 'AliasB', 'AliasC', 'AliasD'])
    check(v.unused_vars, [])


def test_import_alias_use_original(v):
    v.scan(definitions + aliased_imports + uses)
    check(v.defined_classes, ['A', 'B'])
    check(v.defined_funcs, ['C'])
    check(v.defined_imports, ['AliasA', 'AliasB', 'AliasC', 'AliasD'])
    check(v.defined_vars, ['D'])
    check(v.used_names, ['A', 'B', 'C', 'D'])
    check(v.unused_classes, [])
    check(v.unused_funcs, [])
    check(v.unused_imports, ['AliasA', 'AliasB', 'AliasC', 'AliasD'])
    check(v.unused_vars, [])


def test_import_alias_use_alias(v):
    v.scan(definitions + aliased_imports + aliased_uses)
    check(v.defined_classes, ['A', 'B'])
    check(v.defined_funcs, ['C'])
    check(v.defined_imports, ['AliasA', 'AliasB', 'AliasC', 'AliasD'])
    check(v.defined_vars, ['D'])
    check(
        v.used_names,
        ['A', 'B', 'C', 'D', 'AliasA', 'AliasB', 'AliasC', 'AliasD'])
    check(v.unused_classes, [])
    check(v.unused_funcs, [])
    check(v.unused_imports, [])
    check(v.unused_vars, [])
