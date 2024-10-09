from . import check, v

assert v  # Silence pyflakes.


def test_recursion1(v):
    v.scan(
        """\
def Rec():
    Rec()
"""
    )
    check(v.defined_funcs, ["Rec"])
    check(v.unused_funcs, ["Rec"])


def test_recursion2(v):
    v.scan(
        """\
def Rec():
    Rec()

class MyClass:
    def __init__(self):
        pass

    def Rec():
        Rec() # calls global Rec()

def main():
    main()
"""
    )
    check(v.defined_funcs, ["Rec", "Rec", "main"])
    check(v.unused_funcs, ["main"])


def test_recursion3(v):
    v.scan(
        """\
class MyClass:
    def __init__(self):
        pass

    def Rec():
        pass

def Rec():
    MyClass.Rec()
"""
    )
    check(v.defined_funcs, ["Rec", "Rec"])
    check(v.unused_funcs, [])
    # MyClass.Rec() is not treated as a recursive call. So, MyClass.Rec is marked as used, causing Rec to also
    # be marked as used (in Vulture's current behaviour) since they share the same name.


def test_recursion4(v):
    v.scan(
        """\
def Rec():
    Rec()

class MyClass:
    def __init__(self):
        pass

    def Rec():
        pass
"""
    )
    check(v.defined_funcs, ["Rec", "Rec"])
    check(v.unused_funcs, ["Rec", "Rec"])


def test_recursion5(v):
    v.scan(
        """\
def rec():
    if (5 > 4):
        rec()

def outer():
    def inner():
        outer() # these calls aren't considered for recursion
        inner()
"""
    )
    check(v.defined_funcs, ["rec", "outer", "inner"])
    check(v.unused_funcs, ["rec"])
