from wake import Vulture


def test_function_object1():
    v = Vulture()
    v.scan("""\
def func():
    pass

a = func
""")
    assert v.defined_funcs == ['func']
    assert v.unused_funcs == []


def test_function_object2():
    v = Vulture()
    v.scan("""\
def func():
    pass

func
""")
    assert v.defined_funcs == ['func']
    assert v.used_funcs == ['func']
    assert v.unused_funcs == []


def test_function1():
    v = Vulture()
    v.scan("""\
def func1(a):
    pass

def func2(b):
    func1(b)
""")
    # Maybe someday we will support conditional execution and detect func1 too?
    assert v.unused_funcs == ['func2']
    assert v.defined_funcs == ['func1', 'func2']


def test_function2():
    v = Vulture()
    v.scan("""\
def func(a):
    pass

func(5)
""")
    assert v.unused_funcs == []
    assert v.defined_funcs == ['func']


def test_function3():
    v = Vulture()
    v.scan("""\
def foo(a):
    pass

b = foo(5)
""")
    assert v.unused_funcs == []
    assert v.defined_funcs == ['foo']


def test_function_and_method1():
    v = Vulture(verbose=True)
    v.scan("""\
class Bar(object):
    def func(self):
        pass

def func():
    pass

func()
""")
    # TODO: Maybe we can differentiate between method and function use.
    assert v.unused_funcs == ['Bar']
    assert v.defined_funcs == ['Bar', 'func', 'func']


def test_attribute1():
    v = Vulture(verbose=True)
    v.scan("""\
foo.bar = 1
foo.bar = 2
""")
    assert v.unused_funcs == []
    assert v.defined_funcs == []
    assert v.defined_attrs == ['bar', 'bar']
    assert v.used_attrs == []
    assert v.unused_attrs == ['bar']


def test_callback1():
    v = Vulture()
    v.scan("""\
class Bar(object):
    def foo(self):
        pass

b = Bar()
b.foo
""")
    assert v.used_attrs == ['foo']
    assert v.unused_funcs == []
    assert v.defined_funcs == ['Bar', 'foo']


def test_class1():
    v = Vulture()
    v.scan("""\
class Bar(object):
    pass
""")
    assert v.used_attrs == []
    assert v.unused_funcs == ['Bar']
    assert v.defined_funcs == ['Bar']
    assert v.used_funcs == []


def test_class2():
    v = Vulture()
    v.scan("""\
class Bar():
    pass
class Foo(Bar):
    pass
Foo()
""")
    assert v.used_attrs == []
    assert v.unused_funcs == []
    assert v.defined_funcs == ['Bar', 'Foo']
    assert v.used_funcs == ['Bar', 'Foo']


def test_class3():
    v = Vulture()
    v.scan("""\
class Bar():
    pass
[Bar]
""")
    assert v.used_attrs == []
    assert v.defined_funcs == ['Bar']
    assert v.used_funcs == ['Bar']
    assert v.unused_funcs == []


def test_class4():
    v = Vulture()
    v.scan("""\
class Bar():
    pass
Bar()
""")
    assert v.used_attrs == []
    assert v.defined_funcs == ['Bar']
    assert v.used_funcs == ['Bar']
    assert v.unused_funcs == []


def test_class5():
    v = Vulture()
    v.scan("""\
class Bar():
    pass
b = Bar()
""")
    assert v.used_attrs == []
    assert v.defined_funcs == ['Bar']
    assert v.unused_funcs == []


def test_class6():
    v = Vulture()
    v.scan("""\
class Bar():
    pass
a = []
a.insert(0, Bar())
""")
    assert v.defined_funcs == ['Bar']
    assert v.unused_funcs == []


def test_class7():
    v = Vulture()
    v.scan("""\
class Bar(object):
    pass

class Foo(object):
    def __init__(self):
        self.b = xyz.Bar(self)
""")
    assert v.defined_funcs == ['Bar', 'Foo']
    assert v.unused_funcs == ['Foo']


def test_method1():
    v = Vulture()
    v.scan("""\
def __init__(self):
    self.a.foo()

class Bar(object):
    def foo(self):
        pass
""")
    assert v.defined_funcs == ['Bar', 'foo']
    assert v.unused_funcs == ['Bar']


def test_variable1():
    v = Vulture(verbose=True)
    v.scan("a = 1\nb = a")
    assert v.defined_funcs == []
    assert v.used_vars == ['a']
    assert v.defined_vars == ['a', 'b']
    assert v.unused_vars == ['b']


def test_variable2():
    v = Vulture(verbose=True)
    v.scan("a = 1\nc = b.a")
    assert v.defined_funcs == []
    assert v.defined_vars == ['a', 'c']
    assert v.used_vars == ['b']
    assert v.unused_vars == ['c']


def test_variable3():
    v = Vulture(verbose=True)
    v.scan("a = 1\n'%(a)s' % locals()")
    assert v.defined_funcs == []
    assert v.defined_vars == ['a']
    assert v.used_vars == ['a', 'locals']
    assert v.unused_vars == []


def test_variable4():
    v = Vulture(verbose=True)
    v.scan("(a, b), c = (d, e, f)")
    assert v.defined_funcs == []
    assert v.defined_vars == ['a', 'b', 'c']
    assert v.used_vars == ['d', 'e', 'f']
    assert sorted(v.tuple_assign_vars) == ['a', 'b', 'c']
    assert v.unused_vars == []


def test_variable5():
    v = Vulture(verbose=True)
    v.scan("for a, b in func(): a")
    assert v.defined_funcs == []
    assert v.defined_vars == ['a', 'b']
    assert sorted(v.used_vars) == ['a', 'func']
    assert v.tuple_assign_vars == ['a', 'b']
    assert v.unused_vars == []


def test_variable6():
    v = Vulture(verbose=True)
    v.scan("[a for a, b in func()]")
    assert v.defined_vars == ['a', 'b']
    assert sorted(v.used_vars) == ['a', 'func']
    assert v.tuple_assign_vars == ['a', 'b']
    assert v.unused_vars == []


def test_unused_var1():
    v = Vulture(verbose=True)
    v.scan("_a = 1\n__b = 2\n__c__ = 3")
    assert v.defined_vars == []
    assert sorted(v.used_vars) == []
    assert v.unused_vars == []


def test_prop1():
    v = Vulture(verbose=True)
    v.scan("""\
class Bar(object):
    @property
    def prop(self):
        pass

c = Bar()
c.prop
""")
    assert v.defined_funcs == ['Bar']
    assert v.defined_props == ['prop']
    assert v.unused_props == []


def test_prop2():
    v = Vulture(verbose=True)
    v.scan("""\
class Bar(object):
    @property
    def prop(self):
        pass

prop = 1
""")
    assert v.defined_funcs == ['Bar']
    assert v.defined_props == ['prop']
    assert v.unused_props == ['prop']
    assert v.defined_vars == ['prop']


def test_object_attribute():
    v = Vulture(verbose=True)
    v.scan("""\
class Bar(object):
    def __init__(self):
        self.a = []
""")
    assert v.defined_funcs == ['Bar']
    assert v.defined_vars == []
    assert v.defined_attrs == ['a']
    assert v.used_attrs == []
    assert v.unused_attrs == ['a']
