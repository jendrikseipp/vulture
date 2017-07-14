import ast
import pytest
import sys

from vulture.lines import count_lines

PY35 = sys.version_info >= (3, 5)


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

# TODO improve estimate_lines to count the "else" clauses
# and the estimate will get better (higher).


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


def test_size_file():
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


def test_size_multi_line_return():
    example = """
class Foo:
    def long_string_return(o):
        return (
            'very'
            'long'
            'string')
"""
    # We currently cannot handle code ending with multiline statements
    check_size(example, 3)


def test_size_comment_after_last_line():
    example = """
class Foo:
    def bar():
        # A comment.
        pass
        # This comment won't be detected.
"""
    check_size(example, 4)


@pytest.mark.skipif(not PY35, reason='requires Python3.5')
def test_size_generator():
    example = """
class Foo:
    def bar():
        yield something
"""
    check_size(example, 3)


@pytest.mark.skipif(not PY35, reason='requires Python3.5')
def test_size_coroutines_basic():
    example = """
class Foo:
    async def foo(some_attr):
        pass
"""
    check_size(example, 3)


@pytest.mark.skipif(not PY35, reason='requires Python3.5')
def test_size_await():
    example = """
class Foo:
    async def __aenter__(self):
        await log('entering context')

    async def __aexit__(self, exc_type, exc, tb):
        await log('exiting context')
"""
    check_size(example, 6)


@pytest.mark.skipif(not PY35, reason='requires Python3.5')
def test_size_async_with():
    example = """
class Foo:
    async def bar():
        async with x:
            pass
"""
    check_size(example, 4)


@pytest.mark.skipif(not PY35, reason='requires Python3.5')
def test_size_async_for():
    example = """
class Foo:
    async def foo():
        async for a in b: pass
"""
    check_size(example, 3)
