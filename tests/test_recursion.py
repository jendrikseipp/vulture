import sys

from . import check, v, v_rec

assert v
assert v_rec

new_version = sys.version_info.minor >= 9


def test_recursion1(v, v_rec):
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

def Rec5():
    Rec5()

def Rec6():
    Rec6()
"""
    v_rec.scan(code)
    defined_funcs = ["Rec2", "inst2", "Rec5", "Rec6"]
    defined_methods = ["inst", "inst2", "Rec3", "Rec4"]
    check(v_rec.defined_funcs, defined_funcs)
    check(v_rec.defined_methods, defined_methods)
    if new_version:
        check(v_rec.unused_funcs, ["Rec2", "Rec5", "Rec6"])
        check(v_rec.unused_methods, ["inst", "Rec3", "Rec4"])
    else:
        check(v_rec.unused_funcs, [])
        check(v_rec.unused_methods, [])
    v.scan(code)
    check(v.defined_funcs, defined_funcs)
    check(v.unused_funcs, [])
    check(v.defined_methods, defined_methods)
    check(v.unused_methods, [])


def test_recursion2(v, v_rec):
    code = """\
def Rec():
    Rec()

class MyClass:
    def __init__(self):
        pass

    def Rec(self):
        pass
"""
    defined_funcs = ["Rec"]
    defined_methods = ["Rec"]
    v_rec.scan(code)
    check(v_rec.defined_funcs, defined_funcs)
    check(v_rec.defined_methods, defined_methods)
    check(v_rec.unused_funcs, defined_funcs if new_version else [])
    check(v_rec.unused_methods, defined_methods if new_version else [])
    v.scan(code)
    check(v.defined_funcs, defined_funcs)
    check(v.defined_methods, defined_methods)
    check(v.unused_funcs, [])
    check(v.unused_methods, [])


def test_recursion3(v, v_rec):
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

class MyClass:
    def instMethod(self):
        if 5 > 4:
            if 5 > 4:
                self.instMethod()
    def classMethod1():
        if 5 > 4:
            if 5 > 4:
                MyClass.classMethod1()
    @classmethod
    def classMethod2():
        if 5 > 4:
            if 5 > 4:
                MyClass.classMethod2()
    @staticmethod
    def classMethod3():
        if 5 > 4:
            if 5 > 4:
                MyClass.classMethod3()
"""
    v_rec.scan(code)
    defined_funcs = ["rec", "outer", "inner", "classMethod1"]
    defined_methods = ["instMethod", "classMethod2", "classMethod3"]
    check(v_rec.defined_funcs, defined_funcs)
    check(v_rec.defined_methods, defined_methods)
    if new_version:
        check(v_rec.unused_funcs, ["rec", "classMethod1"])
        check(v_rec.unused_methods, defined_methods)
    else:
        check(v_rec.unused_funcs, [])
        check(v_rec.unused_methods, [])
    v.scan(code)
    check(v.defined_funcs, defined_funcs)
    check(v.defined_methods, defined_methods)
    check(v.unused_funcs, [])
    check(v.unused_methods, [])


def test_recursion4(v, v_rec):
    code = """\
def rec(num: int):
    if num > 4:
        x = 1 + (rec ((num + num) / 3) / 2)
        return x
"""
    v_rec.scan(code)
    defined_funcs = ["rec"]
    check(v_rec.defined_funcs, defined_funcs)
    check(v_rec.unused_funcs, defined_funcs if new_version else [])
    v.scan(code)
    check(v.defined_funcs, defined_funcs)
    check(v.unused_funcs, [])


def test_recursion5(v, v_rec):
    code = """\
def rec(num: int):
    for i in (1, num):
        rec(i)
rec(2)

class myClass:
    def instMethod(self, num2):
        for i2 in (1, num2):
            self.instMethod(i2)
        myClass.classMethod1(1)
        myClass.classMethod2(1)
        myClass.classMethod3(1)
    def classMethod1(num3):
        for i3 in (1, num3):
            myClass.classMethod1(i3)
    @classmethod
    def classMethod2(num4):
        for i4 in (1, num4):
            myClass.classMethod2(i4)
    @staticmethod
    def classMethod3(num5):
        for i5 in (1, num5):
            myClass.classMethod3(i5)
o = MyClass()
o.instMethod()
"""
    defined_funcs = ["rec", "classMethod1"]
    defined_methods = ["instMethod", "classMethod2", "classMethod3"]
    defined_vars = [
        "num",
        "i",
        "num2",
        "i2",
        "num3",
        "i3",
        "num4",
        "i4",
        "num5",
        "i5",
        "o",
    ]
    v_rec.scan(code)
    v.scan(code)
    for v_curr in (v_rec, v):
        check(v_curr.defined_funcs, defined_funcs)
        check(v_curr.unused_funcs, [])
        check(v_curr.defined_methods, defined_methods)
        check(v_curr.unused_methods, [])
        check(v_curr.defined_vars, defined_vars)
        check(v_curr.unused_vars, [])
