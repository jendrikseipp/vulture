import ast

import pytest

from vulture import utils


@pytest.fixture
def check_get_decorater_name():
    def check(code, expected_names):
        decorator_names = []

        def visit_FunctionDef(node):
            for decorator in node.decorator_list:
                decorator_names.append(utils.get_decorator_name(decorator))

        node_visitor = ast.NodeVisitor()
        node_visitor.visit_FunctionDef = visit_FunctionDef
        node_visitor.visit(ast.parse(code))
        assert expected_names == decorator_names
    return check


def test_get_decorator_name(check_get_decorater_name):
    code = """\
@foobar
def hoo():
    pass

@xyz()
def bar():
    pass

@x.y.z
def doo():
    pass

@a.b.c.d.foo("Foo and Bar")
def hoofoo():
    pass
"""
    check_get_decorater_name(code, ['foobar', 'xyz', 'x.y.z', 'a.b.c.d.foo'])
