import ast
import os
import pathlib
import sys

import pytest

from vulture import utils


class TestFormatPath:
    @pytest.fixture
    def tmp_cwd(self, tmp_path, monkeypatch):
        cwd = tmp_path / "workingdir"
        cwd.mkdir()
        monkeypatch.chdir(cwd)
        return cwd

    def test_relative_inside(self):
        filepath = pathlib.Path("testfile.py")
        formatted = utils.format_path(filepath)
        assert formatted == filepath
        assert not formatted.is_absolute()

    def test_relative_outside(self, tmp_cwd):
        filepath = pathlib.Path(os.pardir) / "testfile.py"
        formatted = utils.format_path(filepath)
        assert formatted == filepath
        assert not formatted.is_absolute()

    def test_absolute_inside(self, tmp_cwd):
        filepath = tmp_cwd / "testfile.py"
        formatted = utils.format_path(filepath)
        assert formatted == pathlib.Path("testfile.py")
        assert not formatted.is_absolute()

    def test_absolute_outside(self, tmp_cwd):
        filepath = (tmp_cwd / os.pardir / "testfile.py").resolve()
        formatted = utils.format_path(filepath)
        assert formatted == filepath
        assert formatted.is_absolute()


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
    print(request)
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


def test_get_decorator_name_end_function_call():
    code = """\
@foo.bar(x, y, z)
def bar():
    pass
"""
    check_decorator_names(code, ["@foo.bar"])


@pytest.mark.skipif(
    sys.version_info < (3, 9), reason="requires Python 3.9 or higher"
)
@pytest.mark.parametrize(
    "decorated",
    [
        ("def foo():"),
        ("async def foo():"),
        ("class Foo:"),
    ],
)
def test_get_decorator_name_multiple_callables(decorated):
    decorated = f"{decorated}\n    pass"
    code = f"""\
@foo
@bar.prop
@z.func("hi").bar().k.foo
@k("hello").doo("world").x
@k.hello("world")
@foo[2]
{decorated}
"""
    check_decorator_names(
        code,
        ["@foo", "@bar.prop", "@", "@", "@k.hello", "@"],
    )
