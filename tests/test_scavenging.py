from . import check, skip_if_not_has_async, v
assert v  # Silence pyflakes.


def test_function_object1(v):
    v.scan("""\
def func():
    pass

a = func
""")
    check(v.defined_funcs, ['func'])
    check(v.unused_funcs, [])


def test_function_object2(v):
    v.scan("""\
def func():
    pass

func
""")
    check(v.defined_funcs, ['func'])
    check(v.unused_funcs, [])


def test_function1(v):
    v.scan("""\
def func1(a):
    pass

def func2(b):
    func1(b)
""")
    check(v.defined_funcs, ['func1', 'func2'])
    check(v.unused_funcs, ['func2'])


def test_function2(v):
    v.scan("""\
def func(a):
    pass

func(5)
""")
    check(v.unused_funcs, [])
    check(v.defined_funcs, ['func'])


def test_function3(v):
    v.scan("""\
def foo(a):
    pass

b = foo(5)
""")
    check(v.unused_funcs, [])
    check(v.defined_funcs, ['foo'])


@skip_if_not_has_async
def test_async_function(v):
    v.scan("""\
async def foo():
    pass
""")
    check(v.defined_funcs, ['foo'])
    check(v.unused_funcs, ['foo'])


@skip_if_not_has_async
def test_async_method(v):
    v.scan("""\
class Foo:
    async def bar(self):
        pass
""")
    check(v.defined_classes, ['Foo'])
    check(v.defined_funcs, ['bar'])
    check(v.unused_classes, ['Foo'])
    check(v.unused_funcs, ['bar'])


def test_function_and_method1(v):
    v.scan("""\
class Bar(object):
    def func(self):
        pass

def func():
    pass

func()
""")
    check(v.defined_classes, ['Bar'])
    check(v.defined_funcs, ['func', 'func'])
    check(v.unused_classes, ['Bar'])
    check(v.unused_funcs, [])


def test_attribute1(v):
    v.scan("""\
foo.bar = 1
foo.bar = 2
""")
    check(v.unused_funcs, [])
    check(v.defined_funcs, [])
    check(v.defined_attrs, ['bar', 'bar'])
    check(v.used_attrs, [])
    check(v.unused_attrs, ['bar', 'bar'])


def test_ignored_attributes(v):
    v.scan("""\
A._ = 0
A._a = 1
A.__b = 2
A.__c__ = 3
A._d_ = 4
""")
    check(v.defined_attrs, ['_', '_a', '__b', '__c__', '_d_'])
    check(v.used_attrs, [])
    check(v.unused_attrs, ['_', '__b', '__c__', '_a', '_d_'])
    check(v.unused_vars, [])


def test_callback1(v):
    v.scan("""\
class Bar(object):
    def foo(self):
        pass

b = Bar()
b.foo
""")
    check(v.used_attrs, ['foo'])
    check(v.defined_classes, ['Bar'])
    check(v.defined_funcs, ['foo'])
    check(v.unused_classes, [])
    check(v.unused_funcs, [])


def test_class1(v):
    v.scan("""\
class Bar(object):
    pass
""")
    check(v.used_attrs, [])
    check(v.defined_classes, ['Bar'])
    check(v.unused_classes, ['Bar'])


def test_class2(v):
    v.scan("""\
class Bar():
    pass
class Foo(Bar):
    pass
Foo()
""")
    check(v.used_attrs, [])
    check(v.used_names, ['Bar', 'Foo'])
    check(v.defined_classes, ['Bar', 'Foo'])
    check(v.unused_classes, [])


def test_class3(v):
    v.scan("""\
class Bar():
    pass
[Bar]
""")
    check(v.used_attrs, [])
    check(v.used_names, ['Bar'])
    check(v.defined_classes, ['Bar'])
    check(v.unused_classes, [])


def test_class4(v):
    v.scan("""\
class Bar():
    pass
Bar()
""")
    check(v.used_attrs, [])
    check(v.defined_classes, ['Bar'])
    check(v.unused_classes, [])


def test_class5(v):
    v.scan("""\
class Bar():
    pass
b = Bar()
""")
    check(v.used_attrs, [])
    check(v.defined_classes, ['Bar'])
    check(v.unused_classes, [])
    check(v.unused_vars, ['b'])


def test_class6(v):
    v.scan("""\
class Bar():
    pass
a = []
a.insert(0, Bar())
""")
    check(v.defined_classes, ['Bar'])
    check(v.unused_classes, [])


def test_class7(v):
    v.scan("""\
class Bar(object):
    pass

class Foo(object):
    def __init__(self):
        self.b = xyz.Bar(self)
""")
    check(v.defined_classes, ['Bar', 'Foo'])
    check(v.unused_classes, ['Foo'])


def test_method1(v):
    v.scan("""\
def __init__(self):
    self.a.foo()

class Bar(object):
    def foo(self):
        pass
""")
    check(v.defined_classes, ['Bar'])
    check(v.defined_funcs, ['foo'])
    check(v.unused_classes, ['Bar'])
    check(v.unused_funcs, [])


def test_token_types(v):
    v.scan("""\
a
b = 2
c()
x.d
""")
    check(v.defined_funcs, [])
    check(v.defined_vars, ['b'])
    check(v.used_names, ['a', 'c', 'x'])
    check(v.used_attrs, ['d'])
    check(v.unused_attrs, [])
    check(v.unused_funcs, [])
    check(v.unused_props, [])
    check(v.unused_vars, ['b'])


def test_variable1(v):
    v.scan("a = 1\nb = a")
    check(v.defined_funcs, [])
    check(v.used_names, ['a'])
    check(v.defined_vars, ['a', 'b'])
    check(v.unused_vars, ['b'])


def test_variable2(v):
    v.scan("a = 1\nc = b.a")
    check(v.defined_funcs, [])
    check(v.defined_vars, ['a', 'c'])
    check(v.used_names, ['b'])
    check(v.unused_vars, ['c'])


def test_variable3(v):
    v.scan("(a, b), c = (d, e, f)")
    check(v.defined_funcs, [])
    check(v.defined_vars, ['a', 'b', 'c'])
    check(v.used_names, ['d', 'e', 'f'])
    check(v.unused_vars, ['a', 'b', 'c'])


def test_variable4(v):
    v.scan("for a, b in func(): a")
    check(v.defined_funcs, [])
    check(v.defined_vars, ['a', 'b'])
    check(v.used_names, ['a', 'func'])
    check(v.unused_vars, ['b'])


def test_variable5(v):
    v.scan("[a for a, b in func()]")
    check(v.defined_vars, ['a', 'b'])
    check(v.used_names, ['a', 'func'])
    check(v.unused_vars, ['b'])


def test_ignored_variables(v):
    v.scan("""\
_ = 0
_a = 1
__b = 2
__c__ = 3
_d_ = 4
""")
    check(v.defined_vars, ['__b'])
    check(sorted(v.used_names), [])
    check(v.unused_vars, ['__b'])


def test_prop1(v):
    v.scan("""\
class Bar(object):
    @property
    def prop(self):
        pass

c = Bar()
c.prop
""")
    check(v.defined_classes, ['Bar'])
    check(v.defined_props, ['prop'])
    check(v.unused_classes, [])
    check(v.unused_props, [])


def test_prop2(v):
    v.scan("""\
class Bar(object):
    @property
    def prop(self):
        pass

prop = 1
""")
    check(v.defined_classes, ['Bar'])
    check(v.defined_props, ['prop'])
    check(v.defined_vars, ['prop'])
    check(v.unused_classes, ['Bar'])
    check(v.unused_props, ['prop'])


def test_object_attribute(v):
    v.scan("""\
class Bar(object):
    def __init__(self):
        self.a = []
""")
    check(v.defined_attrs, ['a'])
    check(v.defined_classes, ['Bar'])
    check(v.defined_vars, [])
    check(v.used_attrs, [])
    check(v.unused_attrs, ['a'])
    check(v.unused_classes, ['Bar'])


def test_function_names_in_test_file(v):
    v.scan("""\
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
""", filename='test_function_names.py')
    check(v.defined_attrs, [])
    check(v.defined_classes, ['OtherClass'])
    check(v.defined_funcs, ['other_func'])
    check(v.defined_vars, [])
    check(v.used_attrs, [])
    check(v.used_names, [])
    check(v.unused_attrs, [])
    check(v.unused_classes, ['OtherClass'])
    check(v.unused_funcs, ['other_func'])


@skip_if_not_has_async
def test_async_function_name_in_test_file(v):
    v.scan("""\
async def test_func():
    pass

async def other_func():
    pass
""", filename='test_function_names.py')
    check(v.defined_funcs, ['other_func'])
    check(v.unused_funcs, ['other_func'])


@skip_if_not_has_async
def test_async_function_name_in_normal_file(v):
    v.scan("""\
async def test_func():
    pass

async def other_func():
    pass
""", filename='function_names.py')
    check(v.defined_funcs, ['test_func', 'other_func'])
    check(v.unused_funcs, ['other_func', 'test_func'])


def test_function_names_in_normal_file(v):
    v.scan("""\
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
""")
    check(v.defined_attrs, [])
    check(v.defined_classes, ['BasicTestCase', 'OtherClass', 'TestClass'])
    check(v.defined_funcs, ['test_func', 'other_func'])
    check(v.defined_vars, [])
    check(v.used_attrs, [])
    check(v.used_names, [])
    check(v.unused_attrs, [])
    check(v.unused_classes, ['BasicTestCase', 'OtherClass', 'TestClass'])
    check(v.unused_funcs, ['other_func', 'test_func'])


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
    check(v.defined_attrs, ['a'])
    check(v.defined_vars, ['a'])
    check(v.used_attrs, [])
    check(v.used_names, ['a', 'foo'])
    check(v.unused_attrs, ['a'])


def test_boolean(v):
    v.scan("""\
a = True
a
""")
    check(v.defined_vars, ['a'])
    check(v.used_names, ['a'])
    check(v.unused_vars, [])


def test_builtin_types(v):
    v.scan("""\
a = b
a = 1
a = "s"
a = object
a = False
""")
    check(v.defined_vars, ['a'] * 5)
    check(v.used_names, ['b'])
    check(v.unused_vars, ['a'] * 5)


def test_unused_args(v):
    v.scan("""\
def foo(x, y):
    return x + 1
""")
    check(v.defined_vars, ['x', 'y'])
    check(v.used_names, ['x'])
    check(v.unused_vars, ['y'])


def test_unused_kwargs(v):
    v.scan("""\
def foo(x, y=3, **kwargs):
    return x + 1
""")
    check(v.defined_vars, ['kwargs', 'x', 'y'])
    check(v.used_names, ['x'])
    check(v.unused_vars, ['kwargs', 'y'])


def test_unused_kwargs_with_odd_name(v):
    v.scan("""\
def foo(**bar):
    pass
""")
    check(v.defined_vars, ['bar'])
    check(v.used_names, [])
    check(v.unused_vars, ['bar'])


def test_unused_vararg(v):
    v.scan("""\
def foo(*bar):
    pass
""")
    check(v.defined_vars, ['bar'])
    check(v.used_names, [])
    check(v.unused_vars, ['bar'])


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


def test_multiple_definition(v):
    v.scan("""\
a = 1
a = 2
""")
    check(v.defined_vars, ['a', 'a'])
    check(v.used_names, [])
    check(v.unused_vars, ['a', 'a'])
