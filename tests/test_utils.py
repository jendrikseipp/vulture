import ast
from pathlib import PurePath

from vulture import utils
from vulture.utils import format_path
from vulture.config import ABSOLUTE_PATH_FORMAT, RELATIVE_PATH_FORMAT


def check_paths(filename, format_name="relative"):
    assert format_name in (ABSOLUTE_PATH_FORMAT, RELATIVE_PATH_FORMAT)
    pathstr = format_path(filename, None, format_id=format_name)
    pure_path = PurePath(pathstr)
    check = pure_path.is_absolute()
    if format_name == "absolute":
        assert check
    # even if absolute == True, the path might have been specified absolute
    # so can't conclude negatively


def test_absolute_path():
    check_paths(__file__, format_name="absolute")


def test_relative_path():
    check_paths(__file__, format_name="relative")


def check_decorator_names(code, expected_names):
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
    check_decorator_names(code, ["@foobar"])


def test_get_decorator_name_call():
    code = """\
@xyz()
def bar():
    pass
"""
    check_decorator_names(code, ["@xyz"])


def test_get_decorator_name_async():
    code = """\
@foo.bar.route('/foobar')
async def async_function(request):
    print(reques)
"""
    check_decorator_names(code, ["@foo.bar.route"])


def test_get_decorator_name_multiple_attrs():
    code = """\
@x.y.z
def doo():
    pass
"""
    check_decorator_names(code, ["@x.y.z"])


def test_get_decorator_name_multiple_attrs_called():
    code = """\
@a.b.c.d.foo("Foo and Bar")
def hoofoo():
    pass
"""
    check_decorator_names(code, ["@a.b.c.d.foo"])


def test_get_decorator_name_multiple_decorators():
    code = """\
@foo
@bar()
@x.y.z.a('foobar')
def func():
    pass
"""
    check_decorator_names(code, ["@foo", "@bar", "@x.y.z.a"])


def test_get_decorator_name_class():
    code = """\
@foo
@bar.yz
class Foo:
    pass
"""
    check_decorator_names(code, ["@foo", "@bar.yz"])
