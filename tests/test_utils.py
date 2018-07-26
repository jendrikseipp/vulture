import ast

import pytest

from vulture import utils


@pytest.fixture
def check_get_decorator_name():
    def check(code, expected_names):
        decorator_names = []

        def visit_FunctionDef(node):
            for decorator in node.decorator_list:
                decorator_names.append(utils.get_decorator_name(decorator))

        node_visitor = ast.NodeVisitor()
        node_visitor.visit_AsyncFunctionDef = visit_FunctionDef
        node_visitor.visit_ClassDef = visit_FunctionDef
        node_visitor.visit_FunctionDef = visit_FunctionDef
        node_visitor.visit(ast.parse(code))
        assert expected_names == decorator_names
    return check


def test_get_decorator_name_simple(check_get_decorator_name):
    code = """\
@foobar
def hoo():
    pass
"""
    check_get_decorator_name(code, ['foobar'])


def test_get_decorator_name_call(check_get_decorator_name):
    code = """\
@xyz()
def bar():
    pass
"""
    check_get_decorator_name(code, ['xyz'])


def test_get_decorator_name_async(check_get_decorator_name):
    code = """\
@foo.bar.route('/foobar')
async def async_function(request):
    print(reques)
"""
    check_get_decorator_name(code, ['foo.bar.route'])


def test_get_decorator_name_multiple_attrs(check_get_decorator_name):
    code = """\
@x.y.z
def doo():
    pass
"""
    check_get_decorator_name(code, ['x.y.z'])


def test_get_decorator_name_multiple_attrs_called(check_get_decorator_name):
    code = """\
@a.b.c.d.foo("Foo and Bar")
def hoofoo():
    pass
"""
    check_get_decorator_name(code, ['a.b.c.d.foo'])


def test_get_decorator_name_multiple_decorators(check_get_decorator_name):
    code = """\
@foo
@bar()
@x.y.z.a('foobar')
def func():
    pass
"""
    check_get_decorator_name(code, ['foo', 'bar', 'x.y.z.a'])


def test_get_decorator_name_class(check_get_decorator_name):
    code = """\
@foo
@bar.yz
class Foo:
    pass
"""
    check_get_decorator_name(code, ['foo', 'bar.yz'])
