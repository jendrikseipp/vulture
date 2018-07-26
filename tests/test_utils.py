import ast

from . import skip_if_not_has_async
from vulture import utils


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


def test_get_decorator_name_simple():
    code = """\
@foobar
def hoo():
    pass
"""
    check(code, ['foobar'])


def test_get_decorator_name_call():
    code = """\
@xyz()
def bar():
    pass
"""
    check(code, ['xyz'])


@skip_if_not_has_async
def test_get_decorator_name_async():
    code = """\
@foo.bar.route('/foobar')
async def async_function(request):
    print(reques)
"""
    check(code, ['foo.bar.route'])


def test_get_decorator_name_multiple_attrs():
    code = """\
@x.y.z
def doo():
    pass
"""
    check(code, ['x.y.z'])


def test_get_decorator_name_multiple_attrs_called():
    code = """\
@a.b.c.d.foo("Foo and Bar")
def hoofoo():
    pass
"""
    check(code, ['a.b.c.d.foo'])


def test_get_decorator_name_multiple_decorators():
    code = """\
@foo
@bar()
@x.y.z.a('foobar')
def func():
    pass
"""
    check(code, ['foo', 'bar', 'x.y.z.a'])


def test_get_decorator_name_class():
    code = """\
@foo
@bar.yz
class Foo:
    pass
"""
    check(code, ['foo', 'bar.yz'])
