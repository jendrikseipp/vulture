import ast

from vulture.lines import estimate_lines


def check_size(example, span):
    # offset of one because 'node' is ast.Module object
    node = ast.parse(example)
    assert estimate_lines(node) - 1 == span


def test_size_function():
    example = """
def func():
    if "foo" == "bar":
        return "xyz"
    import sys
    return len(sys.argv)
"""
    check_size(example, 5)


def test_size_class():
    example = """
class Foo(object):
    def bar():
        pass

    @staticmethod
    def func():
        if "foo" == "bar":
            return "xyz"
        import sys
        return len(sys.argv)
"""
    check_size(example, 9)

# TODO improve estimate_lines to count the "else" clauses
# and the estimate will get better (higher).


def test_size_if_else():
    example = """
def identity(o):
    return o

@identity
class Foo(object):
    @identity
    @identity
    def bar(self):
        if "a" == "b":
            pass
        elif "b" == "c":
            pass
        else:
            pass
"""
    check_size(example, 12)


def test_size_try_except():
    example = """
try:
    x = sys.argv[99]
except IndexError:
    pass
except Exception:
    pass
else:
    pass
"""
    check_size(example, 7)


def test_size_file():
    example = """
with open("/dev/null") as f:
    f.write("")
"""
    check_size(example, 2)


def test_size_while_else():
    example = """
while "b" > "a":
    pass
else:
    pass
"""
    check_size(example, 3)


def test_size_try_finally():
    example = """
try:
    1/0
finally:
    return 99
"""
    check_size(example, 3)


def test_size_for_else():
    example = """
for arg in sys.argv:
    print("loop")
else:
    print("else")
"""
    check_size(example, 3)
