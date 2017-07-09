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


def test_estimate_lines():
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
        with open("/dev/null") as f:
            f.write("")
        import sys
        while "b" > "a":
            pass
        else:
            pass
        for arg in sys.argv:
            if arg == "foo":
                break
        else:
            pass
        try:
            x = sys.argv[99]
        except IndexError:
            pass
        except Exception:
            pass
        else:
            pass
        try:
            1/0
        finally:
            return 99
"""
    # TODO improve estimate_lines to count the "else" clauses
    # and the estimate will get better (higher).
    check_size(example, 32)
