import ast
import sys

from vulture import lines

from . import skip_if_not_has_async


def get_last_line_number_slow(node):
    """
    A slower, but also simpler and slightly more accurate version of
    get_last_line_number().

    It traverses all descendants of node and records the highest line
    number seen.

    This code is 1.6 times slower than count_lines() on the Python
    subset of tensorflow. It reports the same sizes for all test cases
    and the functions and classes in tensorflow.

    """
    return max(getattr(node, 'lineno', -1) for node in ast.walk(node))


def count_lines(node):
    """Estimate the number of lines of the given AST node."""
    last_lineno = lines.get_last_line_number(node)
    assert get_last_line_number_slow(node) == last_lineno
    return last_lineno - node.lineno + 1


def check_size(example, size):
    tree = ast.parse(example)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == 'Foo':
            assert count_lines(node) == size
            break
    else:
        assert False, 'Failed to find top-level class "Foo" in code'


def test_size_basic():
    example = """
class Foo:
    foo = 1
    bar = 2
"""
    check_size(example, 3)


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
    check_size(example, 10)


def test_size_if_else():
    example = """
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
    check_size(example, 11)


def test_size_while():
    example = """
class Foo:
    while 1:
        print(1)
"""
    check_size(example, 3)


def test_size_while_else():
    example = """
class Foo:
    while "b" > "a":
        pass
    else:
        pass
"""
    check_size(example, 5)


def test_size_with():
    example = """
class Foo:
    with open("/dev/null") as f:
        f.write("")
"""
    check_size(example, 3)


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
    check_size(example, 9)


def test_size_try_finally():
    example = """
class Foo:
    try:
        1/0
    finally:
        return 99
"""
    check_size(example, 5)


def test_size_try_except():
    example = """
class Foo:
    try:
        foo()
    except:
        bar()
"""
    check_size(example, 5)


def test_size_try_excepts():
    example = """
class Foo:
    try:
        foo()
    except IOError:
        bar()
    except AttributeError:
        pass
"""
    check_size(example, 7)


def test_size_for():
    example = """
class Foo:
    for i in range(10):
        print(i)
"""
    check_size(example, 3)


def test_size_for_else():
    example = """
class Foo:
    for arg in sys.argv:
        print("loop")
    else:
        print("else")
"""
    check_size(example, 5)


def test_size_class_nested():
    example = """
class Foo:
    class Bar:
        pass
"""
    check_size(example, 3)


# We currently cannot handle code ending with multiline strings.
def test_size_multi_line_return():
    example = """
class Foo:
    def foo():
        return (
            'very'
            'long'
            'string')
"""
    check_size(example, 4)


# We currently cannot handle code ending with comment lines.
def test_size_comment_after_last_line():
    example = """
class Foo:
    def bar():
        # A comment.
        pass
        # This comment won't be detected.
"""
    check_size(example, 4)


def test_size_generator():
    example = """
class Foo:
    def bar():
        yield something
"""
    check_size(example, 3)


def test_size_exec():
    example = """
class Foo:
    exec('a')
"""
    check_size(example, 2)


def test_size_print1():
    example = """
class Foo:
    print(
        'foo')
"""
    check_size(example, 3)


def test_size_print2():
    example = """
class Foo:
    print(
        'foo',)
"""
    check_size(example, 3)


def test_size_return():
    example = """
class Foo:
    return (True and
        False)
"""
    check_size(example, 3)


def test_size_import_from():
    example = """
class Foo:
    from a import b
"""
    check_size(example, 2)


def test_size_delete():
    example = """
class Foo:
    del a[:
        foo()]
"""
    check_size(example, 3)


def test_size_list_comprehension():
    example = """
class Foo:
    [a
     for a in
     b]
"""
    check_size(example, 4)


# We currently cannot handle closing brackets on a separate line.
def test_size_list():
    example = """
class Foo:
    [a, b
    ]
"""
    check_size(example, 2)


# We currently cannot handle code ending with an ellipsis on Python 2.
def test_size_ellipsis():
    example = """
class Foo:
    bar[1:2,
        ...]
"""
    if sys.version_info < (3, 0):
        check_size(example, 2)
    else:
        # ast.Ellipsis is a subclass of ast.expr in Python 3.
        check_size(example, 3)


def test_size_starargs():
    example = """
class Foo:
    def foo():
        bar(*a,
            b=c)
"""
    check_size(example, 4)


# If we add a line break between a and b, the code is too greedy and moves
# down to the slice which has no line numbers. If we took b or c into
# account, the line count would be correct.
def test_size_assign():
    example = """
class Foo:
    bar = foo(a, b)[c,:]
"""
    check_size(example, 2)


@skip_if_not_has_async
def test_size_async_function_def():
    example = """
class Foo:
    async def foo(some_attr):
        pass
"""
    check_size(example, 3)


@skip_if_not_has_async
def test_size_async_with():
    example = """
class Foo:
    async def bar():
        async with x:
            pass
"""
    check_size(example, 4)


@skip_if_not_has_async
def test_size_async_for():
    example = """
class Foo:
    async def foo():
        async for a in b:
            pass
"""
    check_size(example, 4)
