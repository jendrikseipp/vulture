from vulture import Vulture


FUNCTION_OBJECT1 = """\
def func():
    pass

a = func
"""
def test_function_object1():
    v = Vulture()
    v.scan(FUNCTION_OBJECT1)
    assert v.defined_funcs == ['func']
    assert v.unused_funcs == []


FUNCTION_OBJECT2 = """\
def func():
    pass

func
"""
def test_function_object2():
    v = Vulture()
    v.scan(FUNCTION_OBJECT2)
    assert v.defined_funcs == ['func']
    assert v.used_funcs == ['func']
    assert v.unused_funcs == []


FUNCTION1 = """\
def func1(a):
    pass

def func2(b):
    func1(b)
"""
def test_function1():
    v = Vulture()
    v.scan(FUNCTION1)
    # Maybe someday we will support conditional execution and detect func1 too?
    assert v.unused_funcs == ['func2']
    assert v.defined_funcs == ['func1', 'func2']


FUNCTION2 = """\
def func(a):
    pass

func(5)
"""
def test_function2():
    v = Vulture()
    v.scan(FUNCTION2)
    assert v.unused_funcs == []
    assert v.defined_funcs == ['func']


FUNCTION3 = """\
def foo(a):
    pass

b = foo(5)
"""
def test_function3():
    v = Vulture()
    v.scan(FUNCTION3)
    assert v.unused_funcs == []
    assert v.defined_funcs == ['foo']


CALLBACK1 = """\
class Bar(object):
    def foo(self):
        pass

b = Bar()
b.foo
"""
def test_callback1():
    v = Vulture()
    v.scan(CALLBACK1)
    assert v.used_attrs == ['foo']
    assert v.unused_funcs == []
    assert v.defined_funcs == ['Bar', 'foo']

CLASS1 = """\
class Bar(object):
    pass
"""
def test_class1():
    v = Vulture()
    v.scan(CLASS1)
    assert v.used_attrs == []
    assert v.unused_funcs == ['Bar']
    assert v.defined_funcs == ['Bar']
    assert v.used_funcs == []

CLASS2 = """\
class Bar():
    pass
class Foo(Bar):
    pass
Foo()
"""
def test_class2():
    v = Vulture()
    v.scan(CLASS2)
    assert v.used_attrs == []
    assert v.unused_funcs == []
    assert v.defined_funcs == ['Bar', 'Foo']
    assert v.used_funcs == ['Bar', 'Foo']

CLASS3 = """\
class Bar():
    pass
[Bar]
"""
def test_class3():
    v = Vulture()
    v.scan(CLASS3)
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

def test_class6():
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
    v.scan("for a, b in func(): print a")
    assert v.defined_funcs == []
    assert v.defined_vars == ['a', 'b']
    assert sorted(v.used_vars) == ['a', 'func']
    assert v.tuple_assign_vars == ['a', 'b']
    assert v.unused_vars == []
