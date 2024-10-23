import sys

from . import check, v, v_rec

assert v
assert v_rec

new_version = sys.version_info.minor >= 9


def test_recursion1(v, v_rec):
    code = """\
def Rec():
    Rec()
"""
    v_rec.scan(code)
    if new_version:
        check(v_rec.defined_funcs, ["Rec"])
        check(v_rec.unused_funcs, ["Rec"])
    else:
        check(v_rec.defined_funcs, ["Rec"])
        check(v_rec.unused_funcs, [])
    v.scan(code)
    check(v.defined_funcs, ["Rec"])
    check(v.unused_funcs, [])


def test_recursion2(v, v_rec):
    code = """\
class MyClass:
    def __init__(self):
        pass

    def inst(self):
        self.inst()

    def inst2(self):
        self.inst2()

    def Rec2():
        MyClass.Rec2()

    @classmethod
    def Rec3():
        MyClass.Rec3()

    @staticmethod
    def Rec4():
        MyClass.Rec4()

def inst2():
    o = MyClass()
    o.inst2()

def Rec3():
    Rec3()

def Rec4():
    Rec4()
"""
    v_rec.scan(code)
    if new_version:
        check(v_rec.defined_funcs, ["Rec2", "inst2", "Rec3", "Rec4"])
        check(v_rec.unused_funcs, ["Rec2", "Rec3", "Rec4"])
        check(v_rec.defined_methods, ["inst", "inst2", "Rec3", "Rec4"])
        check(v_rec.unused_methods, ["inst", "Rec3", "Rec4"])
    else:
        check(v_rec.defined_funcs, ["Rec2", "inst2", "Rec3", "Rec4"])
        check(v_rec.unused_funcs, [])
        check(v_rec.defined_methods, ["inst", "inst2", "Rec3", "Rec4"])
        check(v_rec.unused_methods, [])
    v.scan(code)
    check(v.defined_funcs, ["Rec2", "inst2", "Rec3", "Rec4"])
    check(v.unused_funcs, [])
    check(v.defined_methods, ["inst", "inst2", "Rec3", "Rec4"])
    check(v.unused_methods, [])


def test_recursion3(v, v_rec):
    code = """\
class MyClass:
    def __init__(self):
        pass

    @classmethod
    def Rec():
        MyClass.Rec()

def aa():
    aa()
"""
    v_rec.scan(code)
    check(
        v_rec.defined_funcs,
        [
            "aa",
        ],
    )
    if new_version:
        check(v_rec.defined_methods, ["Rec"])
        check(v_rec.unused_funcs, ["aa"])
        check(v_rec.unused_methods, ["Rec"])
    else:
        check(v_rec.defined_methods, ["Rec"])
        check(v_rec.unused_funcs, [])
        check(v_rec.unused_methods, [])

    v.scan(code)
    check(
        v.defined_funcs,
        [
            "aa",
        ],
    )
    check(v.defined_methods, ["Rec"])
    check(v.unused_funcs, [])
    check(v.unused_methods, [])


def test_recursion4(v, v_rec):
    code = """\
def Rec():
    Rec()

class MyClass:
    def __init__(self):
        pass

    def Rec():
        pass
"""
    v_rec.scan(code)
    if new_version:
        check(v_rec.defined_funcs, ["Rec", "Rec"])
        check(v_rec.unused_funcs, ["Rec", "Rec"])
    else:
        check(v_rec.defined_funcs, ["Rec", "Rec"])
        check(v_rec.unused_funcs, [])
    v.scan(code)
    check(v.defined_funcs, ["Rec", "Rec"])
    check(v.unused_funcs, [])


def test_recursion5(v, v_rec):
    code = """\
def rec():
    if 5 > 4:
        if 5 > 4:
            rec()

def outer():
    def inner():
        # the following calls are within a function within a function, so they
        # are disregarded from recursion candidacy (to keep things simple)
        outer()
        inner()
"""
    v_rec.scan(code)
    if new_version:
        check(v_rec.defined_funcs, ["rec", "outer", "inner"])
        check(v_rec.unused_funcs, ["rec"])
    else:
        check(v_rec.defined_funcs, ["rec", "outer", "inner"])
        check(v_rec.unused_funcs, [])
    v.scan(code)
    check(v.defined_funcs, ["rec", "outer", "inner"])
    check(v.unused_funcs, [])


def test_recursion6(v, v_rec):
    code = """\
def rec(num: int):
    if num > 4:
        x = 1 + (rec ((num + num) / 3) / 2)
        return x
"""
    v_rec.scan(code)
    if new_version:
        check(v_rec.defined_funcs, ["rec"])
        check(v_rec.unused_funcs, ["rec"])
    else:
        check(v_rec.defined_funcs, ["rec"])
        check(v_rec.unused_funcs, [])
    v.scan(code)
    check(v.defined_funcs, ["rec"])
    check(v.unused_funcs, [])


def test_recursion7(v, v_rec):
    code = """\
def rec(num: int):
    for i in (1, num):
        rec(i)
rec(2)
"""
    v_rec.scan(code)
    check(v_rec.defined_funcs, ["rec"])
    check(v_rec.unused_funcs, [])
    check(v_rec.defined_vars, ["num", "i"])
    check(v_rec.unused_vars, [])
    v.scan(code)
    check(v.defined_funcs, ["rec"])
    check(v.unused_funcs, [])
    check(v.defined_vars, ["num", "i"])
    check(v.unused_vars, [])
