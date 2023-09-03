import sys

import pytest

from . import check, v
from vulture.utils import ExitCode

assert v  # Silence pyflakes.


def test_function_object1(v):
    v.scan(
        """\
def func():
    pass

a = func
"""
    )
    check(v.defined_funcs, ["func"])
    check(v.unused_funcs, [])


def test_function_object2(v):
    v.scan(
        """\
def func():
    pass

func
"""
    )
    check(v.defined_funcs, ["func"])
    check(v.unused_funcs, [])


def test_function1(v):
    v.scan(
        """\
def func1(a):
    pass

def func2(b):
    func1(b)
"""
    )
    check(v.defined_funcs, ["func1", "func2"])
    check(v.unused_funcs, ["func2"])


def test_function2(v):
    v.scan(
        """\
def func(a):
    pass

func(5)
"""
    )
    check(v.unused_funcs, [])
    check(v.defined_funcs, ["func"])


def test_function3(v):
    v.scan(
        """\
def foo(a):
    pass

b = foo(5)
"""
    )
    check(v.unused_funcs, [])
    check(v.defined_funcs, ["foo"])


def test_async_function(v):
    v.scan(
        """\
async def foo():
    pass
"""
    )
    check(v.defined_funcs, ["foo"])
    check(v.unused_funcs, ["foo"])


def test_async_method(v):
    v.scan(
        """\
class Foo:
    async def bar(self):
        pass
"""
    )
    check(v.defined_classes, ["Foo"])
    check(v.defined_funcs, [])
    check(v.defined_methods, ["bar"])
    check(v.unused_classes, ["Foo"])
    check(v.unused_methods, ["bar"])


def test_function_and_method1(v):
    v.scan(
        """\
class Bar(object):
    def func(self):
        pass

def func():
    pass

func()
"""
    )
    check(v.defined_classes, ["Bar"])
    check(v.defined_funcs, ["func"])
    check(v.defined_methods, ["func"])
    check(v.unused_classes, ["Bar"])
    check(v.unused_funcs, [])
    # Bar.func is unused, but it's hard to detect this without producing a
    # false positive in test_function_and_method2.
    check(v.unused_methods, [])


def test_function_and_method2(v):
    v.scan(
        """\
class Bar(object):
    def func(self):
        pass

    other_name_for_func = func

Bar().other_name_for_func()
"""
    )
    check(v.defined_classes, ["Bar"])
    check(v.defined_funcs, [])
    check(v.defined_methods, ["func"])
    check(v.defined_vars, ["other_name_for_func"])
    check(v.unused_classes, [])
    check(v.unused_funcs, [])
    check(v.unused_methods, [])
    check(v.unused_vars, [])


def test_attribute1(v):
    v.scan(
        """\
foo.bar = 1
foo.bar = 2
"""
    )
    check(v.unused_funcs, [])
    check(v.defined_funcs, [])
    check(v.defined_attrs, ["bar", "bar"])
    check(v.used_names, ["foo"])
    check(v.unused_attrs, ["bar", "bar"])


def test_ignored_attributes(v):
    v.scan(
        """\
A._ = 0
A._a = 1
A.__b = 2
A.__c__ = 3
A._d_ = 4
"""
    )
    check(v.defined_attrs, ["_", "_a", "__b", "__c__", "_d_"])
    check(v.used_names, ["A"])
    check(v.unused_attrs, ["_", "__b", "__c__", "_a", "_d_"])
    check(v.unused_vars, [])


def test_getattr(v):
    v.scan(
        """\
class Thing:
    used_attr1 = 1
    used_attr2 = 2
    used_attr3 = 3
    unused_attr = 4

getattr(Thing, "used_attr1")
getattr(Thing, "used_attr2", None)
hasattr(Thing, "used_attr3")

# Weird calls ignored
hasattr(Thing, "unused_attr", None)
getattr(Thing)
getattr("unused_attr")
getattr(Thing, "unused_attr", 1, 2)
"""
    )
    check(v.unused_vars, ["unused_attr"])
    check(
        v.used_names,
        [
            "Thing",
            "getattr",
            "hasattr",
            "used_attr1",
            "used_attr2",
            "used_attr3",
        ],
    )


def test_callback1(v):
    v.scan(
        """\
class Bar(object):
    def foo(self):
        pass

b = Bar()
b.foo
"""
    )
    check(v.used_names, ["Bar", "b", "foo"])
    check(v.defined_classes, ["Bar"])
    check(v.defined_funcs, [])
    check(v.defined_methods, ["foo"])
    check(v.unused_classes, [])
    check(v.unused_funcs, [])


def test_class1(v):
    v.scan(
        """\
class Bar(object):
    pass
"""
    )
    check(v.used_names, [])
    check(v.defined_classes, ["Bar"])
    check(v.unused_classes, ["Bar"])


def test_class2(v):
    v.scan(
        """\
class Bar():
    pass
class Foo(Bar):
    pass
Foo()
"""
    )
    check(v.used_names, ["Bar", "Foo"])
    check(v.defined_classes, ["Bar", "Foo"])
    check(v.unused_classes, [])


def test_class3(v):
    v.scan(
        """\
class Bar():
    pass
[Bar]
"""
    )
    check(v.used_names, ["Bar"])
    check(v.defined_classes, ["Bar"])
    check(v.unused_classes, [])


def test_class4(v):
    v.scan(
        """\
class Bar():
    pass
Bar()
"""
    )
    check(v.used_names, ["Bar"])
    check(v.defined_classes, ["Bar"])
    check(v.unused_classes, [])


def test_class5(v):
    v.scan(
        """\
class Bar():
    pass
b = Bar()
"""
    )
    check(v.used_names, ["Bar"])
    check(v.defined_classes, ["Bar"])
    check(v.unused_classes, [])
    check(v.unused_vars, ["b"])


def test_class6(v):
    v.scan(
        """\
class Bar():
    pass
a = []
a.insert(0, Bar())
"""
    )
    check(v.defined_classes, ["Bar"])
    check(v.unused_classes, [])


def test_class7(v):
    v.scan(
        """\
class Bar(object):
    pass

class Foo(object):
    def __init__(self):
        self.b = xyz.Bar(self)
"""
    )
    check(v.defined_classes, ["Bar", "Foo"])
    check(v.unused_classes, ["Foo"])


def test_method1(v):
    v.scan(
        """\
def __init__(self):
    self.a.foo()

class Bar(object):
    def foo(self):
        pass

    @classmethod
    def bar(cls):
        pass

    @staticmethod
    def foobar():
        pass
"""
    )
    check(v.defined_classes, ["Bar"])
    check(v.defined_funcs, [])
    check(v.defined_methods, ["foo", "bar", "foobar"])
    check(v.unused_classes, ["Bar"])
    check(v.unused_funcs, [])
    check(v.unused_methods, ["bar", "foobar"])


def test_token_types(v):
    v.scan(
        """\
a
b = 2
c()
x.d
"""
    )
    check(v.defined_funcs, [])
    check(v.defined_vars, ["b"])
    check(v.used_names, ["a", "c", "d", "x"])
    check(v.unused_attrs, [])
    check(v.unused_funcs, [])
    check(v.unused_props, [])
    check(v.unused_vars, ["b"])


def test_variable1(v):
    v.scan("a = 1\nb = a")
    check(v.defined_funcs, [])
    check(v.used_names, ["a"])
    check(v.defined_vars, ["a", "b"])
    check(v.unused_vars, ["b"])


def test_variable2(v):
    v.scan("a = 1\nc = b.a")
    check(v.defined_funcs, [])
    check(v.defined_vars, ["a", "c"])
    check(v.used_names, ["a", "b"])
    check(v.unused_vars, ["c"])


def test_variable3(v):
    v.scan("(a, b), c = (d, e, f)")
    check(v.defined_funcs, [])
    check(v.defined_vars, ["a", "b", "c"])
    check(v.used_names, ["d", "e", "f"])
    check(v.unused_vars, ["a", "b", "c"])


def test_variable4(v):
    v.scan("for a, b in func(): a")
    check(v.defined_funcs, [])
    check(v.defined_vars, ["a", "b"])
    check(v.used_names, ["a", "func"])
    check(v.unused_vars, ["b"])


def test_variable5(v):
    v.scan("[a for a, b in func()]")
    check(v.defined_vars, ["a", "b"])
    check(v.used_names, ["a", "func"])
    check(v.unused_vars, ["b"])


def test_ignored_variables(v):
    v.scan(
        """\
_ = 0
_a = 1
__b = 2
__c__ = 3
_d_ = 4
"""
    )
    check(v.defined_vars, ["__b"])
    check(sorted(v.used_names), [])
    check(v.unused_vars, ["__b"])


def test_prop1(v):
    v.scan(
        """\
class Bar(object):
    @property
    def prop(self):
        pass

c = Bar()
c.prop
"""
    )
    check(v.defined_classes, ["Bar"])
    check(v.defined_props, ["prop"])
    check(v.unused_classes, [])
    check(v.unused_props, [])


def test_prop2(v):
    v.scan(
        """\
class Bar(object):
    @property
    def prop(self):
        pass

prop = 1
"""
    )
    check(v.defined_classes, ["Bar"])
    check(v.defined_props, ["prop"])
    check(v.defined_vars, ["prop"])
    check(v.unused_classes, ["Bar"])
    check(v.unused_props, ["prop"])


def test_object_attribute(v):
    v.scan(
        """\
class Bar(object):
    def __init__(self):
        self.a = []
"""
    )
    check(v.defined_attrs, ["a"])
    check(v.defined_classes, ["Bar"])
    check(v.defined_vars, [])
    check(v.used_names, [])
    check(v.unused_attrs, ["a"])
    check(v.unused_classes, ["Bar"])


def test_function_names_in_test_file(v):
    v.scan(
        """\
def setup_module(module):
    module

def teardown_module(module):
    module

def setup_function(function):
    function

def teardown_function(function):
    function

def test_func():
    pass

def other_func():
    pass

class TestClass:
    @classmethod
    def setup_class(cls):
        cls

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        method

    def teardown_method(self, method):
        pass

class BasicTestCase:
    pass

class OtherClass:
    pass
""",
        filename="dir/test_function_names.py",
    )
    check(v.defined_attrs, [])
    check(v.defined_classes, ["OtherClass"])
    check(v.defined_funcs, ["other_func"])
    check(v.defined_methods, [])
    check(
        v.defined_vars,
        [
            "cls",
            "cls",
            "function",
            "function",
            "method",
            "method",
            "module",
            "module",
        ],
    )
    check(v.used_names, ["classmethod", "cls", "function", "method", "module"])
    check(v.unused_attrs, [])
    check(v.unused_classes, ["OtherClass"])
    check(v.unused_funcs, ["other_func"])
    check(v.unused_methods, [])
    check(v.unused_vars, [])


def test_async_function_name_in_test_file(v):
    v.scan(
        """\
async def test_func():
    pass

async def other_func():
    pass
""",
        filename="dir/test_function_names.py",
    )
    check(v.defined_funcs, ["other_func"])
    check(v.unused_funcs, ["other_func"])


def test_async_function_name_in_normal_file(v):
    v.scan(
        """\
async def test_func():
    pass

async def other_func():
    pass
""",
        filename="dir/function_names.py",
    )
    check(v.defined_funcs, ["test_func", "other_func"])
    check(v.unused_funcs, ["other_func", "test_func"])


def test_function_names_in_normal_file(v):
    v.scan(
        """\
def test_func():
    pass

def other_func():
    pass

class TestClass:
    pass

class BasicTestCase:
    pass

class OtherClass:
    pass
"""
    )
    check(v.defined_attrs, [])
    check(v.defined_classes, ["BasicTestCase", "OtherClass", "TestClass"])
    check(v.defined_funcs, ["test_func", "other_func"])
    check(v.defined_vars, [])
    check(v.used_names, [])
    check(v.unused_attrs, [])
    check(v.unused_classes, ["BasicTestCase", "OtherClass", "TestClass"])
    check(v.unused_funcs, ["other_func", "test_func"])


def test_global_attribute(v):
    v.scan(
        """\
# Module foo:
a = 1
if a == 1:
    pass

# Module bar:
import foo
foo.a = 2
"""
    )
    check(v.defined_attrs, ["a"])
    check(v.defined_vars, ["a"])
    check(v.used_names, ["a", "foo"])
    check(v.unused_attrs, [])


def test_boolean(v):
    v.scan(
        """\
a = True
a
"""
    )
    check(v.defined_vars, ["a"])
    check(v.used_names, ["a"])
    check(v.unused_vars, [])


def test_builtin_types(v):
    v.scan(
        """\
a = b
a = 1
a = "s"
a = object
a = False
"""
    )
    check(v.defined_vars, ["a"] * 5)
    check(v.used_names, ["b"])
    check(v.unused_vars, ["a"] * 5)


def test_unused_args(v):
    v.scan(
        """\
def foo(x, y):
    return x + 1
"""
    )
    check(v.defined_vars, ["x", "y"])
    check(v.used_names, ["x"])
    check(v.unused_vars, ["y"])


def test_unused_kwargs(v):
    v.scan(
        """\
def foo(x, y=3, **kwargs):
    return x + 1
"""
    )
    check(v.defined_vars, ["kwargs", "x", "y"])
    check(v.used_names, ["x"])
    check(v.unused_vars, ["kwargs", "y"])


def test_unused_kwargs_with_odd_name(v):
    v.scan(
        """\
def foo(**bar):
    pass
"""
    )
    check(v.defined_vars, ["bar"])
    check(v.used_names, [])
    check(v.unused_vars, ["bar"])


def test_unused_vararg(v):
    v.scan(
        """\
def foo(*bar):
    pass
"""
    )
    check(v.defined_vars, ["bar"])
    check(v.used_names, [])
    check(v.unused_vars, ["bar"])


def test_multiple_definition(v):
    v.scan(
        """\
a = 1
a = 2
"""
    )
    check(v.defined_vars, ["a", "a"])
    check(v.used_names, [])
    check(v.unused_vars, ["a", "a"])


def test_arg_type_annotation(v):
    v.scan(
        """\
from typing import Iterable

def f(n: int) -> Iterable[int]:
    yield n
"""
    )

    check(v.unused_vars, [])
    check(v.unused_funcs, ["f"])
    check(v.unused_imports, [])


def test_var_type_annotation(v):
    v.scan(
        """\
from typing import List

x: List[int] = [1]
"""
    )

    check(v.unused_vars, ["x"])
    check(v.unused_funcs, [])
    check(v.unused_imports, [])


def test_type_hint_comments(v):
    v.scan(
        """\
from typing import Any, Dict, List, Text, Tuple


def plain_function(arg):
    # type: (Text) -> None
    pass

async def async_function(arg):
    # type: (List[int]) -> None
    pass

some_var = {}  # type: Dict[str, str]

class Thing:
    def __init__(self):
        self.some_attr = (1, 2)  # type: Tuple[int, int]

for x in []:  # type: Any
    print(x)
"""
    )

    check(v.unused_imports, [])
    assert v.exit_code == ExitCode.NoDeadCode


def test_invalid_type_comment(v):
    v.scan(
        """\
def bad():
    # type: bogus
    pass
bad()
"""
    )

    assert v.exit_code == ExitCode.InvalidInput


def test_unused_args_with_del(v):
    v.scan(
        """\
def foo(a, b, c, d=3):
    del c, d
    return a + b

foo(1, 2)
"""
    )

    check(v.defined_funcs, ["foo"])
    check(v.defined_vars, ["a", "b", "c", "d"])
    check(v.used_names, ["foo", "a", "b", "c", "d"])
    check(v.unused_vars, [])
    check(v.unused_funcs, [])


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="requires python3.10 or higher"
)
def test_match_class_simple(v):
    v.scan(
        """\
from dataclasses import dataclass


@dataclass
class X:
    a: int
    b: int
    c: int
    u: int

x = input()

match x:
    case X(a=0):
        print("a")
    case X(b=0, c=0):
        print("b c")
"""
    )
    check(v.defined_classes, ["X"])
    check(v.defined_vars, ["a", "b", "c", "u", "x"])

    check(v.unused_classes, [])
    check(v.unused_vars, ["u"])


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="requires python3.10 or higher"
)
def test_match_class_embedded(v):
    v.scan(
        """\
from dataclasses import dataclass


@dataclass
class X:
    a: int
    b: int
    c: int
    d: int
    e: int
    u: int

x = input()

match x:
    case X(a=1) | X(b=0):
        print("Or")
    case [X(c=1), X(d=0)]:
        print("Sequence")
    case {"k": X(e=1)}:
        print("Mapping")
"""
    )
    check(v.defined_classes, ["X"])
    check(v.defined_vars, ["a", "b", "c", "d", "e", "u", "x"])

    check(v.unused_classes, [])
    check(v.unused_vars, ["u"])


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="requires python3.10 or higher"
)
def test_match_enum(v):
    v.scan(
        """\
from enum import Enum


class Color(Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2
    BLUE = 3

color = input()

match color:
    case Color.RED:
        print("Real danger!")
    case Color.YELLOW | Color.GREEN:
        print("No danger!")
"""
    )
    check(v.defined_classes, ["Color"])
    check(v.defined_vars, ["RED", "YELLOW", "GREEN", "BLUE", "color"])

    check(v.unused_classes, [])
    check(v.unused_vars, ["BLUE"])
