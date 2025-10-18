import ast
import os
import pathlib

import pytest

from vulture import utils


class TestIsValidModuleName:
    def test_valid_lowercase(self):
        assert utils._is_valid_module_name("module")

    def test_valid_with_underscores(self):
        assert utils._is_valid_module_name("my_module")

    def test_valid_with_numbers(self):
        assert utils._is_valid_module_name("module2")
        assert utils._is_valid_module_name("my_module_123")

    def test_valid_starting_with_underscore(self):
        assert utils._is_valid_module_name("_private")
        assert utils._is_valid_module_name("__init__")

    def test_invalid_starting_with_dot(self):
        assert not utils._is_valid_module_name(".module")

    def test_invalid_emacs_temp_file(self):
        assert not utils._is_valid_module_name(".#module")

    def test_invalid_starting_with_number(self):
        assert not utils._is_valid_module_name("2module")

    def test_invalid_with_dash(self):
        assert not utils._is_valid_module_name("my-module")

    def test_invalid_with_special_chars(self):
        assert not utils._is_valid_module_name("my@module")
        assert not utils._is_valid_module_name("my$module")
        assert not utils._is_valid_module_name("my!module")

    def test_invalid_empty(self):
        assert not utils._is_valid_module_name("")


class TestGetModules:
    def test_get_modules_filters_invalid_names(self, tmp_path):
        # Create files with valid and invalid names
        valid_file = tmp_path / "valid_module.py"
        valid_file.write_text("def foo(): pass")

        emacs_temp = tmp_path / ".#valid_module.py"
        emacs_temp.write_text("def bar(): pass")

        invalid_with_dash = tmp_path / "my-module.py"
        invalid_with_dash.write_text("def baz(): pass")

        invalid_start_num = tmp_path / "2module.py"
        invalid_start_num.write_text("def qux(): pass")

        # Get modules from the directory
        modules = utils.get_modules([tmp_path])

        # Only the valid module should be included
        assert len(modules) == 1
        assert modules[0].name == "valid_module.py"

    def test_get_modules_explicit_file_with_invalid_name(self, tmp_path):
        # When explicitly specifying a file, it should still be included
        # even if the name is invalid (user knows what they're doing)
        invalid_file = tmp_path / ".#test.py"
        invalid_file.write_text("def foo(): pass")

        modules = utils.get_modules([invalid_file])

        # Explicitly specified file should be included
        assert len(modules) == 1
        assert modules[0].name == ".#test.py"

    def test_get_modules_valid_underscore_names(self, tmp_path):
        # Test various valid module names
        files = [
            "_private.py",
            "__init__.py",
            "module_123.py",
            "valid_module.py",
        ]

        for filename in files:
            (tmp_path / filename).write_text("def foo(): pass")

        modules = utils.get_modules([tmp_path])

        # All files should be included
        assert len(modules) == len(files)
        module_names = {m.name for m in modules}
        assert module_names == set(files)


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


@pytest.mark.parametrize(
    "decorated",
    [
        "def foo():",
        "async def foo():",
        "class Foo:",
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
