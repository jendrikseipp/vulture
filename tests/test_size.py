import ast

from vulture.lines import estimate_lines, count_lines


def check_size(example, size):
    # offset of one because 'node' is ast.Module object
    node = ast.parse(example)
    assert estimate_lines(node) - 1 == size


def check_span(example, span):
    tree = ast.parse(example)
    results = []
    for node in tree.body:
        results.append(count_lines(node))
    assert span == results


def test_size_function():
    example = """
def func():
    if "foo" == "bar":
        return "xyz"
    import sys
    return len(sys.argv)
"""
    check_size(example, 5)
    check_span(example, [5])


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
    check_span(example, [10])

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
    check_span(example, [2, 11])


def test_size_while_else():
    example = """
class Foo:
    while "b" > "a":
        pass
    else:
        pass
"""
    check_size(example, 4)
    check_span(example, [5])


def test_size_file():
    example = """
class Foo:
    with open("/dev/null") as f:
        f.write("")
"""
    check_size(example, 3)
    check_span(example, [3])


def test_size_try_except_else():
    example = """
class Foo:
    try:
        x = sys.argv[99]
    except IndexError:
        pass
    except Exception:
        pass
    else:
        pass
"""
    check_size(example, 8)
    check_span(example, [9])


def test_size_try_finally():
    example = """
class Foo:
    try:
        1/0
    finally:
        return 99
"""
    check_size(example, 4)
    check_span(example, [5])


def test_size_try_except():
    example = """
class Foo:
    try:
        foo()
    except:
        bar()
"""
    check_size(example, 5)
    check_span(example, [5])


def test_size_for_else():
    example = """
class Foo:
    for arg in sys.argv:
        print("loop")
    else:
        print("else")
"""
    check_size(example, 4)
    check_span(example, [5])


def test_size_class_nested():
    example = """
class Foo:
    class test:
        pass
"""
    check_span(example, [3])
