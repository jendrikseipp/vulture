import pytest

from vulture import Vulture


@pytest.fixture
def v():
    return Vulture(verbose=True)


def test_function_object1(v):
    v.scan("""\
def func():
    pass

a = func
""")
    assert v.defined_funcs == ['func']
    assert v.unused_funcs == []


def test_function_object2(v):
    v.scan("""\
def func():
    pass

func
""")
    assert v.defined_funcs == ['func']
    assert v.unused_funcs == []


def test_function1(v):
    v.scan("""\
def func1(a):
    pass

def func2(b):
    func1(b)
""")
    assert v.defined_funcs == ['func1', 'func2']
    assert v.unused_funcs == ['func2']


def test_function2(v):
    v.scan("""\
def func(a):
    pass

func(5)
""")
    assert v.unused_funcs == []
    assert v.defined_funcs == ['func']


def test_function3(v):
    v.scan("""\
def foo(a):
    pass

b = foo(5)
""")
    assert v.unused_funcs == []
    assert v.defined_funcs == ['foo']


def test_function_and_method1(v):
    v.scan("""\
class Bar(object):
    def func(self):
        pass

def func():
    pass

func()
""")
    assert v.defined_classes == ['Bar']
    assert v.defined_funcs == ['func', 'func']
    assert v.unused_classes == ['Bar']
    assert v.unused_funcs == []


def test_attribute1(v):
    v.scan("""\
foo.bar = 1
foo.bar = 2
""")
    assert v.unused_funcs == []
    assert v.defined_funcs == []
    assert v.defined_attrs == ['bar', 'bar']
    assert v.used_attrs == []
    assert v.unused_attrs == ['bar']


def test_callback1(v):
    v.scan("""\
class Bar(object):
    def foo(self):
        pass

b = Bar()
b.foo
""")
    assert v.used_attrs == ['foo']
    assert v.defined_classes == ['Bar']
    assert v.defined_funcs == ['foo']
    assert v.unused_classes == []
    assert v.unused_funcs == []


def test_class1(v):
    v.scan("""\
class Bar(object):
    pass
""")
    assert v.used_attrs == []
    assert v.defined_classes == ['Bar']
    assert v.unused_classes == ['Bar']


def test_class2(v):
    v.scan("""\
class Bar():
    pass
class Foo(Bar):
    pass
Foo()
""")
    assert v.used_attrs == []
    assert v.used_vars == ['Bar', 'Foo']
    assert v.defined_classes == ['Bar', 'Foo']
    assert v.unused_classes == []


def test_class3(v):
    v.scan("""\
class Bar():
    pass
[Bar]
""")
    assert v.used_attrs == []
    assert v.used_vars == ['Bar']
    assert v.defined_classes == ['Bar']
    assert v.unused_classes == []


def test_class4(v):
    v.scan("""\
class Bar():
    pass
Bar()
""")
    assert v.used_attrs == []
    assert v.defined_classes == ['Bar']
    assert v.unused_classes == []


def test_class5(v):
    v.scan("""\
class Bar():
    pass
b = Bar()
""")
    assert v.used_attrs == []
    assert v.defined_classes == ['Bar']
    assert v.unused_classes == []
    assert v.unused_vars == ['b']


def test_class6(v):
    v.scan("""\
class Bar():
    pass
a = []
a.insert(0, Bar())
""")
    assert v.defined_classes == ['Bar']
    assert v.unused_classes == []


def test_class7(v):
    v.scan("""\
class Bar(object):
    pass

class Foo(object):
    def __init__(self):
        self.b = xyz.Bar(self)
""")
    assert v.defined_classes == ['Bar', 'Foo']
    assert v.unused_classes == ['Foo']


def test_method1(v):
    v.scan("""\
def __init__(self):
    self.a.foo()

class Bar(object):
    def foo(self):
        pass
""")
    assert v.defined_classes == ['Bar']
    assert v.defined_funcs == ['foo']
    assert v.unused_classes == ['Bar']
    assert v.unused_funcs == []


def test_token_types(v):
    v.scan("""\
a
b = 2
c()
x.d
""")
    assert v.defined_funcs == []
    assert v.defined_vars == ['b']
    assert v.used_vars == ['a', 'c', 'x']
    assert v.used_attrs == ['d']
    assert v.unused_attrs == []
    assert v.unused_funcs == []
    assert v.unused_props == []
    assert v.unused_vars == ['b']


def test_variable1(v):
    v.scan("a = 1\nb = a")
    assert v.defined_funcs == []
    assert v.used_vars == ['a']
    assert v.defined_vars == ['a', 'b']
    assert v.unused_vars == ['b']


def test_variable2(v):
    v.scan("a = 1\nc = b.a")
    assert v.defined_funcs == []
    assert v.defined_vars == ['a', 'c']
    assert v.used_vars == ['b']
    assert v.unused_vars == ['c']


def test_variable3(v):
    v.scan("(a, b), c = (d, e, f)")
    assert v.defined_funcs == []
    assert v.defined_vars == ['a', 'b', 'c']
    assert v.used_vars == ['d', 'e', 'f']
    assert sorted(v.tuple_assign_vars) == ['a', 'b', 'c']
    assert v.unused_vars == []


def test_variable4(v):
    v.scan("for a, b in func(): a")
    assert v.defined_funcs == []
    assert v.defined_vars == ['a', 'b']
    assert sorted(v.used_vars) == ['a', 'func']
    assert v.tuple_assign_vars == ['a', 'b']
    assert v.unused_vars == []


def test_variable5(v):
    v.scan("[a for a, b in func()]")
    assert v.defined_vars == ['a', 'b']
    assert sorted(v.used_vars) == ['a', 'func']
    assert v.tuple_assign_vars == ['a', 'b']
    assert v.unused_vars == []


def test_ignored_variables(v):
    v.scan("""\
_ = 0
_a = 1
__b = 2
__c__ = 3
_d_ = 4
""")
    assert v.defined_vars == ['__b']
    assert sorted(v.used_vars) == []
    assert v.unused_vars == ['__b']


def test_prop1(v):
    v.scan("""\
class Bar(object):
    @property
    def prop(self):
        pass

c = Bar()
c.prop
""")
    assert v.defined_classes == ['Bar']
    assert v.defined_props == ['prop']
    assert v.unused_classes == []
    assert v.unused_props == []


def test_prop2(v):
    v.scan("""\
class Bar(object):
    @property
    def prop(self):
        pass

prop = 1
""")
    assert v.defined_classes == ['Bar']
    assert v.defined_props == ['prop']
    assert v.defined_vars == ['prop']
    assert v.unused_classes == ['Bar']
    assert v.unused_props == ['prop']


def test_object_attribute(v):
    v.scan("""\
class Bar(object):
    def __init__(self):
        self.a = []
""")
    assert v.defined_attrs == ['a']
    assert v.defined_classes == ['Bar']
    assert v.defined_vars == []
    assert v.used_attrs == []
    assert v.unused_attrs == ['a']
    assert v.unused_classes == ['Bar']


def test_function_names_in_test_file(v):
    v.scan("""\
def test_func():
    pass

def other_func():
    pass

class TestClass:
    pass

class OtherClass:
    pass
""", filename='test_function_names.py')
    assert v.defined_attrs == []
    assert v.defined_classes == ['OtherClass']
    assert v.defined_funcs == ['other_func']
    assert v.defined_vars == []
    assert v.used_attrs == []
    assert v.used_vars == []
    assert v.unused_attrs == []
    assert v.unused_classes == ['OtherClass']
    assert v.unused_funcs == ['other_func']


def test_function_names_in_normal_file(v):
    v.scan("""\
def test_func():
    pass

def other_func():
    pass

class TestClass:
    pass

class OtherClass:
    pass
""")
    assert v.defined_attrs == []
    assert v.defined_classes == ['TestClass', 'OtherClass']
    assert v.defined_funcs == ['test_func', 'other_func']
    assert v.defined_vars == []
    assert v.used_attrs == []
    assert v.used_vars == []
    assert v.unused_attrs == []
    assert v.unused_classes == ['OtherClass', 'TestClass']
    assert v.unused_funcs == ['other_func', 'test_func']


def test_global_attribute(v):
    v.scan("""\
# Module foo:
a = 1
if a == 1:
    pass

# Module bar:
import foo
foo.a = 2
""")
    assert v.defined_attrs == ['a']
    assert v.defined_vars == ['a']
    assert v.used_attrs == []
    assert v.used_vars == ['a', 'foo']
    assert v.unused_attrs == []


def test_boolean(v):
    v.scan("""\
a = True
a
""")
    assert v.defined_vars == ['a']
    assert v.used_vars == ['a']
    assert v.unused_vars == []


def test_builtin_types(v):
    v.scan("""\
a = b
a = 1
a = "s"
a = object
a = False
""")
    assert v.defined_vars == ['a'] * 5
    assert v.used_vars == ['b']
    assert v.unused_vars == ['a']


def test_unused_args(v):
    v.scan("""\
def foo(x, y):
    return x + 1
""")
    assert v.defined_vars == ['x', 'y']
    assert v.used_vars == ['x']
    assert v.unused_vars == ['y']


def test_unused_kwargs(v):
    v.scan("""\
def foo(x, y=3, **kwargs):
    return x + 1
""")
    assert set(v.defined_vars) == set(['kwargs', 'x', 'y'])
    assert v.used_vars == ['x']
    assert v.unused_vars == ['kwargs', 'y']


def test_unused_kwargs_with_odd_name(v):
    v.scan("""\
def foo(**bar):
    pass
""")
    assert v.defined_vars == ['bar']
    assert v.used_vars == []
    assert v.unused_vars == ['bar']


def test_unused_vararg(v):
    v.scan("""\
def foo(*bar):
    pass
""")
    assert v.defined_vars == ['bar']
    assert v.used_vars == []
    assert v.unused_vars == ['bar']


def test_encoding1(v):
    v.scan(u"""\
# -*- coding: utf-8 -*-
pass
""")
    assert True


def test_encoding2(v):
    v.scan(u"""\
#! /usr/bin/env python
# -*- coding: utf-8 -*-
pass
""")
    assert True
