import ast
from fnmatch import fnmatch, fnmatchcase
from pathlib import Path
import pkgutil
import re
import string
import sys

from vulture import lines
from vulture import noqa
from vulture import utils
from vulture.config import make_config


DEFAULT_CONFIDENCE = 60

IGNORED_VARIABLE_NAMES = {"object", "self"}
PYTEST_FUNCTION_NAMES = {
    "setup_module",
    "teardown_module",
    "setup_function",
    "teardown_function",
}
PYTEST_METHOD_NAMES = {
    "setup_class",
    "teardown_class",
    "setup_method",
    "teardown_method",
}

ERROR_CODES = {
    "attribute": "V101",
    "class": "V102",
    "function": "V103",
    "import": "V104",
    "method": "V105",
    "property": "V106",
    "variable": "V107",
    "unreachable_code": "V201",
}


def _get_unused_items(defined_items, used_names):
    unused_items = [
        item for item in set(defined_items) if item.name not in used_names
    ]
    unused_items.sort(key=lambda item: item.name.lower())
    return unused_items


def _is_special_name(name):
    return name.startswith("__") and name.endswith("__")


def _match(name, patterns, case=True):
    func = fnmatchcase if case else fnmatch
    return any(func(name, pattern) for pattern in patterns)


def _is_test_file(filename):
    return _match(
        filename.resolve(),
        ["*/test/*", "*/tests/*", "*/test*.py", "*[-_]test.py"],
        case=False,
    )


def _assigns_special_variable__all__(node):
    assert isinstance(node, ast.Assign)
    return isinstance(node.value, (ast.List, ast.Tuple)) and any(
        target.id == "__all__"
        for target in node.targets
        if isinstance(target, ast.Name)
    )


def _ignore_class(filename, class_name):
    return _is_test_file(filename) and "Test" in class_name


def _ignore_import(filename, import_name):
    """
    Ignore star-imported names since we can't detect whether they are used.
    Ignore imports from __init__.py files since they're commonly used to
    collect objects from a package.
    """
    return filename.name == "__init__.py" or import_name == "*"


def _ignore_function(filename, function_name):
    return (
        function_name in PYTEST_FUNCTION_NAMES
        or function_name.startswith("test_")
    ) and _is_test_file(filename)


def _ignore_method(filename, method_name):
    return _is_special_name(method_name) or (
        (method_name in PYTEST_METHOD_NAMES or method_name.startswith("test_"))
        and _is_test_file(filename)
    )


def _ignore_variable(filename, varname):
    """
    Ignore _ (Python idiom), _x (pylint convention) and
    __x__ (special variable or method), but not __x.
    """
    return (
        varname in IGNORED_VARIABLE_NAMES
        or (varname.startswith("_") and not varname.startswith("__"))
        or _is_special_name(varname)
    )


class Item:
    """
    Hold the name, type and location of defined code.
    """

    __slots__ = (
        "name",
        "typ",
        "filename",
        "first_lineno",
        "last_lineno",
        "message",
        "confidence",
    )

    def __init__(
        self,
        name,
        typ,
        filename,
        first_lineno,
        last_lineno,
        message="",
        confidence=DEFAULT_CONFIDENCE,
    ):
        self.name = name
        self.typ = typ
        self.filename = filename
        self.first_lineno = first_lineno
        self.last_lineno = last_lineno
        self.message = message or f"unused {typ} '{name}'"
        self.confidence = confidence

    @property
    def size(self):
        assert self.last_lineno >= self.first_lineno
        return self.last_lineno - self.first_lineno + 1

    def get_report(self, add_size=False):
        if add_size:
            line_format = "line" if self.size == 1 else "lines"
            size_report = f", {self.size:d} {line_format}"
        else:
            size_report = ""
        return "{}:{:d}: {} ({}% confidence{})".format(
            utils.format_path(self.filename),
            self.first_lineno,
            self.message,
            self.confidence,
            size_report,
        )

    def get_whitelist_string(self):
        filename = utils.format_path(self.filename)
        if self.typ == "unreachable_code":
            return f"# {self.message} ({filename}:{self.first_lineno})"
        else:
            prefix = ""
            if self.typ in ["attribute", "method", "property"]:
                prefix = "_."
            return "{}{}  # unused {} ({}:{:d})".format(
                prefix, self.name, self.typ, filename, self.first_lineno
            )

    def _tuple(self):
        return (self.filename, self.first_lineno, self.name)

    def __repr__(self):
        return repr(self.name)

    def __eq__(self, other):
        return self._tuple() == other._tuple()

    def __hash__(self):
        return hash(self._tuple())


class Vulture(ast.NodeVisitor):
    """Find dead code."""

    def __init__(
        self, verbose=False, ignore_names=None, ignore_decorators=None
    ):
        self.verbose = verbose

        def get_list(typ):
            return utils.LoggingList(typ, self.verbose)

        self.defined_attrs = get_list("attribute")
        self.defined_classes = get_list("class")
        self.defined_funcs = get_list("function")
        self.defined_imports = get_list("import")
        self.defined_methods = get_list("method")
        self.defined_props = get_list("property")
        self.defined_vars = get_list("variable")
        self.unreachable_code = get_list("unreachable_code")

        self.used_names = utils.LoggingSet("name", self.verbose)

        self.ignore_names = ignore_names or []
        self.ignore_decorators = ignore_decorators or []

        self.filename = Path()
        self.code = []
        self.found_dead_code_or_error = False

    def scan(self, code, filename=""):
        filename = Path(filename)
        self.code = code.splitlines()
        self.noqa_lines = noqa.parse_noqa(self.code)
        self.filename = filename

        def handle_syntax_error(e):
            text = f' at "{e.text.strip()}"' if e.text else ""
            print(
                f"{utils.format_path(filename)}:{e.lineno}: {e.msg}{text}",
                file=sys.stderr,
            )
            self.found_dead_code_or_error = True

        try:
            node = (
                ast.parse(
                    code, filename=str(self.filename), type_comments=True
                )
                if sys.version_info >= (3, 8)  # type_comments requires 3.8+
                else ast.parse(code, filename=str(self.filename))
            )
        except SyntaxError as err:
            handle_syntax_error(err)
        except ValueError as err:
            # ValueError is raised if source contains null bytes.
            print(
                f'{utils.format_path(filename)}: invalid source code "{err}"',
                file=sys.stderr,
            )
            self.found_dead_code_or_error = True
        else:
            # When parsing type comments, visiting can throw SyntaxError.
            try:
                self.visit(node)
            except SyntaxError as err:
                handle_syntax_error(err)

    def scavenge(self, paths, exclude=None):
        def prepare_pattern(pattern):
            if not any(char in pattern for char in "*?["):
                pattern = f"*{pattern}*"
            return pattern

        exclude = [prepare_pattern(pattern) for pattern in (exclude or [])]

        def exclude_path(path):
            return _match(path, exclude, case=False)

        paths = [Path(path) for path in paths]

        for module in utils.get_modules(paths):
            if exclude_path(module):
                self._log("Excluded:", module)
                continue

            self._log("Scanning:", module)
            try:
                module_string = utils.read_file(module)
            except utils.VultureInputException as err:  # noqa: F841
                print(
                    f"Error: Could not read file {module} - {err}\n"
                    f"Try to change the encoding to UTF-8.",
                    file=sys.stderr,
                )
                self.found_dead_code_or_error = True
            else:
                self.scan(module_string, filename=module)

        unique_imports = {item.name for item in self.defined_imports}
        for import_name in unique_imports:
            path = Path("whitelists") / (import_name + "_whitelist.py")
            if exclude_path(path):
                self._log("Excluded whitelist:", path)
            else:
                try:
                    module_data = pkgutil.get_data("vulture", str(path))
                    self._log("Included whitelist:", path)
                except OSError:
                    # Most imported modules don't have a whitelist.
                    continue
                module_string = module_data.decode("utf-8")
                self.scan(module_string, filename=path)

    def get_unused_code(self, min_confidence=0, sort_by_size=False):
        """
        Return ordered list of unused Item objects.
        """
        if not 0 <= min_confidence <= 100:
            raise ValueError("min_confidence must be between 0 and 100.")

        def by_name(item):
            return (str(item.filename).lower(), item.first_lineno)

        def by_size(item):
            return (item.size,) + by_name(item)

        unused_code = (
            self.unused_attrs
            + self.unused_classes
            + self.unused_funcs
            + self.unused_imports
            + self.unused_methods
            + self.unused_props
            + self.unused_vars
            + self.unreachable_code
        )

        confidently_unused = [
            obj for obj in unused_code if obj.confidence >= min_confidence
        ]

        return sorted(
            confidently_unused, key=by_size if sort_by_size else by_name
        )

    def report(
        self, min_confidence=0, sort_by_size=False, make_whitelist=False
    ):
        """
        Print ordered list of Item objects to stdout.
        """
        for item in self.get_unused_code(
            min_confidence=min_confidence, sort_by_size=sort_by_size
        ):
            print(
                item.get_whitelist_string()
                if make_whitelist
                else item.get_report(add_size=sort_by_size)
            )
            self.found_dead_code_or_error = True
        return self.found_dead_code_or_error

    @property
    def unused_classes(self):
        return _get_unused_items(self.defined_classes, self.used_names)

    @property
    def unused_funcs(self):
        return _get_unused_items(self.defined_funcs, self.used_names)

    @property
    def unused_imports(self):
        return _get_unused_items(self.defined_imports, self.used_names)

    @property
    def unused_methods(self):
        return _get_unused_items(self.defined_methods, self.used_names)

    @property
    def unused_props(self):
        return _get_unused_items(self.defined_props, self.used_names)

    @property
    def unused_vars(self):
        return _get_unused_items(self.defined_vars, self.used_names)

    @property
    def unused_attrs(self):
        return _get_unused_items(self.defined_attrs, self.used_names)

    def _log(self, *args):
        if self.verbose:
            print(*args)

    def _add_aliases(self, node):
        """
        We delegate to this method instead of using visit_alias() to have
        access to line numbers and to filter imports from __future__.
        """
        assert isinstance(node, (ast.Import, ast.ImportFrom))
        for name_and_alias in node.names:
            # Store only top-level module name ("os.path" -> "os").
            # We can't easily detect when "os.path" is used.
            name = name_and_alias.name.partition(".")[0]
            alias = name_and_alias.asname
            self._define(
                self.defined_imports,
                alias or name,
                node,
                confidence=90,
                ignore=_ignore_import,
            )
            if alias is not None:
                self.used_names.add(name_and_alias.name)

    def _handle_conditional_node(self, node, name):
        if utils.condition_is_always_false(node.test):
            self._define(
                self.unreachable_code,
                name,
                node,
                last_node=node.body
                if isinstance(node, ast.IfExp)
                else node.body[-1],
                message=f"unsatisfiable '{name}' condition",
                confidence=100,
            )
        elif utils.condition_is_always_true(node.test):
            else_body = node.orelse
            if name == "ternary":
                self._define(
                    self.unreachable_code,
                    name,
                    else_body,
                    message="unreachable 'else' expression",
                    confidence=100,
                )
            elif else_body:
                self._define(
                    self.unreachable_code,
                    "else",
                    else_body[0],
                    last_node=else_body[-1],
                    message="unreachable 'else' block",
                    confidence=100,
                )
            elif name == "if":
                # Redundant if-condition without else block.
                self._define(
                    self.unreachable_code,
                    name,
                    node,
                    message="redundant if-condition",
                    confidence=100,
                )

    def _define(
        self,
        collection,
        name,
        first_node,
        last_node=None,
        message="",
        confidence=DEFAULT_CONFIDENCE,
        ignore=None,
    ):
        def ignored(lineno):
            return (
                (ignore and ignore(self.filename, name))
                or _match(name, self.ignore_names)
                or noqa.ignore_line(self.noqa_lines, lineno, ERROR_CODES[typ])
            )

        last_node = last_node or first_node
        typ = collection.typ
        first_lineno = lines.get_first_line_number(first_node)

        if ignored(first_lineno):
            self._log(f'Ignoring {typ} "{name}"')
        else:
            last_lineno = lines.get_last_line_number(last_node)
            collection.append(
                Item(
                    name,
                    typ,
                    self.filename,
                    first_lineno,
                    last_lineno,
                    message=message,
                    confidence=confidence,
                )
            )

    def _define_variable(self, name, node, confidence=DEFAULT_CONFIDENCE):
        self._define(
            self.defined_vars,
            name,
            node,
            confidence=confidence,
            ignore=_ignore_variable,
        )

    def visit_arg(self, node):
        """Function argument"""
        self._define_variable(node.arg, node, confidence=100)

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Store):
            self._define(self.defined_attrs, node.attr, node)
        elif isinstance(node.ctx, ast.Load):
            self.used_names.add(node.attr)

    def visit_BinOp(self, node):
        """
        Parse variable names in old format strings:

        "%(my_var)s" % locals()
        """
        if (
            isinstance(node.left, ast.Str)
            and isinstance(node.op, ast.Mod)
            and self._is_locals_call(node.right)
        ):
            self.used_names |= set(re.findall(r"%\((\w+)\)", node.left.s))

    def visit_Call(self, node):
        # Count getattr/hasattr(x, "some_attr", ...) as usage of some_attr.
        if isinstance(node.func, ast.Name) and (
            (node.func.id == "getattr" and 2 <= len(node.args) <= 3)
            or (node.func.id == "hasattr" and len(node.args) == 2)
        ):
            attr_name_arg = node.args[1]
            if isinstance(attr_name_arg, ast.Str):
                self.used_names.add(attr_name_arg.s)

        # Parse variable names in new format strings:
        # "{my_var}".format(**locals())
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Str)
            and node.func.attr == "format"
            and any(
                kw.arg is None and self._is_locals_call(kw.value)
                for kw in node.keywords
            )
        ):
            self._handle_new_format_string(node.func.value.s)

    def _handle_new_format_string(self, s):
        def is_identifier(name):
            return bool(re.match(r"[a-zA-Z_][a-zA-Z0-9_]*", name))

        parser = string.Formatter()
        try:
            names = [name for _, name, _, _ in parser.parse(s) if name]
        except ValueError:
            # Invalid format string.
            names = []

        for field_name in names:
            # Remove brackets and their contents: "a[0][b].c[d].e" -> "a.c.e",
            # then split the resulting string: "a.b.c" -> ["a", "b", "c"]
            vars = re.sub(r"\[\w*\]", "", field_name).split(".")
            for var in vars:
                if is_identifier(var):
                    self.used_names.add(var)

    @staticmethod
    def _is_locals_call(node):
        """Return True if the node is `locals()`."""
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "locals"
            and not node.args
            and not node.keywords
        )

    def visit_ClassDef(self, node):
        for decorator in node.decorator_list:
            if _match(
                utils.get_decorator_name(decorator), self.ignore_decorators
            ):
                self._log(
                    f'Ignoring class "{node.name}" (decorator whitelisted)'
                )
                break
        else:
            self._define(
                self.defined_classes, node.name, node, ignore=_ignore_class
            )

    def visit_FunctionDef(self, node):
        decorator_names = [
            utils.get_decorator_name(decorator)
            for decorator in node.decorator_list
        ]

        first_arg = node.args.args[0].arg if node.args.args else None

        if "@property" in decorator_names:
            typ = "property"
        elif (
            "@staticmethod" in decorator_names
            or "@classmethod" in decorator_names
            or first_arg == "self"
        ):
            typ = "method"
        else:
            typ = "function"

        if any(
            _match(name, self.ignore_decorators) for name in decorator_names
        ):
            self._log(f'Ignoring {typ} "{node.name}" (decorator whitelisted)')
        elif typ == "property":
            self._define(self.defined_props, node.name, node)
        elif typ == "method":
            self._define(
                self.defined_methods, node.name, node, ignore=_ignore_method
            )
        else:
            self._define(
                self.defined_funcs, node.name, node, ignore=_ignore_function
            )

    def visit_If(self, node):
        self._handle_conditional_node(node, "if")

    def visit_IfExp(self, node):
        self._handle_conditional_node(node, "ternary")

    def visit_Import(self, node):
        self._add_aliases(node)

    def visit_ImportFrom(self, node):
        if node.module != "__future__":
            self._add_aliases(node)

    def visit_Name(self, node):
        if (
            isinstance(node.ctx, (ast.Load, ast.Del))
            and node.id not in IGNORED_VARIABLE_NAMES
        ):
            self.used_names.add(node.id)
        elif isinstance(node.ctx, (ast.Param, ast.Store)):
            self._define_variable(node.id, node)

    def visit_Assign(self, node):
        if _assigns_special_variable__all__(node):
            assert isinstance(node.value, (ast.List, ast.Tuple))
            for elt in node.value.elts:
                if isinstance(elt, ast.Str):
                    self.used_names.add(elt.s)

    def visit_While(self, node):
        self._handle_conditional_node(node, "while")

    def visit_MatchClass(self, node):
        for kwd_attr in node.kwd_attrs:
            self.used_names.add(kwd_attr)

    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, None)
        if self.verbose:
            lineno = getattr(node, "lineno", 1)
            line = self.code[lineno - 1] if self.code else ""
            self._log(lineno, ast.dump(node), line)
        if visitor:
            visitor(node)

        # There isn't a clean subset of node types that might have type
        # comments, so just check all of them.
        type_comment = getattr(node, "type_comment", None)
        if type_comment is not None:
            mode = (
                "func_type"
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                else "eval"
            )
            self.visit(
                ast.parse(type_comment, filename="<type_comment>", mode=mode)
            )

        return self.generic_visit(node)

    def _handle_ast_list(self, ast_list):
        """
        Find unreachable nodes in the given sequence of ast nodes.
        """
        for index, node in enumerate(ast_list):
            if isinstance(
                node, (ast.Break, ast.Continue, ast.Raise, ast.Return)
            ):
                try:
                    first_unreachable_node = ast_list[index + 1]
                except IndexError:
                    continue
                class_name = node.__class__.__name__.lower()
                self._define(
                    self.unreachable_code,
                    class_name,
                    first_unreachable_node,
                    last_node=ast_list[-1],
                    message=f"unreachable code after '{class_name}'",
                    confidence=100,
                )
                return

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        for _, value in ast.iter_fields(node):
            if isinstance(value, list):
                self._handle_ast_list(value)
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item)
            elif isinstance(value, ast.AST):
                self.visit(value)


def main():
    config = make_config()
    vulture = Vulture(
        verbose=config["verbose"],
        ignore_names=config["ignore_names"],
        ignore_decorators=config["ignore_decorators"],
    )
    vulture.scavenge(config["paths"], exclude=config["exclude"])
    sys.exit(
        vulture.report(
            min_confidence=config["min_confidence"],
            sort_by_size=config["sort_by_size"],
            make_whitelist=config["make_whitelist"],
        )
    )
