#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# vulture - Find dead code.
#
# Copyright (c) 2012-2018 Jendrik Seipp (jendrikseipp@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function

import argparse
import ast
from fnmatch import fnmatch, fnmatchcase
import os.path
import pkgutil
import re
import string
import sys

from vulture import lines
from vulture import utils

__version__ = '0.29'

DEFAULT_CONFIDENCE = 60

# The ast module in Python 2 trips over "coding" cookies, so strip them.
ENCODING_REGEX = re.compile(
    r"^[ \t\v]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+).*?$", flags=re.M)

IGNORED_VARIABLE_NAMES = set(['object', 'self'])
# True and False are NameConstants since Python 3.4.
if sys.version_info < (3, 4):
    IGNORED_VARIABLE_NAMES |= set(['True', 'False'])


def _get_unused_items(defined_items, used_names):
    unused_items = [item for item in set(defined_items)
                    if item.name not in used_names]
    unused_items.sort(key=lambda item: item.name.lower())
    return unused_items


def _is_special_name(name):
    return name.startswith('__') and name.endswith('__')


def _is_test_file(filename):
    return any(
        fnmatch(os.path.basename(filename), pattern)
        for pattern in ['test*.py', '*_test.py', '*-test.py'])


def _ignore_class(filename, class_name):
    return _is_test_file(filename) and 'Test' in class_name


def _ignore_import(_filename, import_name):
    # Ignore star-imported names, since we can't detect whether they are used.
    return import_name == '*'


def _ignore_function(filename, function_name):
    return (
        _is_special_name(function_name) or
        (function_name.startswith('test_') and _is_test_file(filename)))


def _ignore_variable(filename, varname):
    """
    Ignore _ (Python idiom), _x (pylint convention) and
    __x__ (special variable or method), but not __x.
    """
    return (
        varname in IGNORED_VARIABLE_NAMES or
        (varname.startswith('_') and not varname.startswith('__')) or
        _is_special_name(varname))


class Item(object):
    """
    Hold the name, type and location of defined code.
    """

    def __init__(self, name, typ, filename, first_lineno, last_lineno,
                 message='',
                 confidence=DEFAULT_CONFIDENCE):
        self.name = name
        self.typ = typ
        self.filename = filename
        self.first_lineno = first_lineno
        self.last_lineno = last_lineno
        self.message = message or "unused {typ} '{name}'".format(**locals())
        self.confidence = confidence

    @property
    def size(self):
        assert self.last_lineno >= self.first_lineno
        return self.last_lineno - self.first_lineno + 1

    def get_report(self, add_size=False):
        if add_size:
            line_format = 'line' if self.size == 1 else 'lines'
            size_report = ', {0:d} {1}'.format(self.size, line_format)
        else:
            size_report = ''
        return "{0}:{1:d}: {2} ({3}% confidence{4})".format(
            utils.format_path(self.filename), self.first_lineno,
            self.message, self.confidence, size_report)

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

    def __init__(self, verbose=False, ignore_names=None):
        self.verbose = verbose

        def get_list(typ):
            return utils.LoggingList(typ, self.verbose)

        def get_set(typ):
            return utils.LoggingSet(typ, self.verbose)

        self.defined_attrs = get_list('attribute')
        self.defined_classes = get_list('class')
        self.defined_funcs = get_list('function')
        self.defined_imports = get_list('import')
        self.defined_props = get_list('property')
        self.defined_vars = get_list('variable')
        self.unreachable_code = get_list('unreachable_code')

        self.used_attrs = get_set('attribute')
        self.used_names = get_set('name')

        self.ignore_names = ignore_names or []

        self.filename = ''
        self.code = []
        self.found_dead_code_or_error = False

    def scan(self, code, filename=''):
        code = ENCODING_REGEX.sub("", code, count=1)
        self.code = code.splitlines()
        self.filename = filename
        try:
            node = ast.parse(code, filename=self.filename)
        except SyntaxError as err:
            text = ' at "{0}"'.format(err.text.strip()) if err.text else ''
            print('{0}:{1:d}: {2}{3}'.format(
                utils.format_path(filename), err.lineno, err.msg, text),
                file=sys.stderr)
            self.found_dead_code_or_error = True
        except (TypeError, ValueError) as err:
            # Python < 3.5 raises TypeError and Python >= 3.5 raises
            # ValueError if source contains null bytes.
            print('{0}: invalid source code "{1}"'.format(
                utils.format_path(filename), err), file=sys.stderr)
            self.found_dead_code_or_error = True
        else:
            self.visit(node)

    def scavenge(self, paths, exclude=None):
        def prepare_pattern(pattern):
            if not any(char in pattern for char in ['*', '?', '[']):
                pattern = '*{pattern}*'.format(**locals())
            return pattern

        exclude = [prepare_pattern(pattern) for pattern in (exclude or [])]

        def exclude_file(name):
            return any(fnmatch(name, pattern) for pattern in exclude)

        for module in utils.get_modules(paths):
            if exclude_file(module):
                self._log('Excluded:', module)
                continue

            self._log('Scanning:', module)
            try:
                module_string = utils.read_file(module)
            except utils.VultureInputException as err:
                print(
                    'Error: Could not read file {module} - {err}\n'
                    'Try to change the encoding to UTF-8.'.format(**locals()),
                    file=sys.stderr)
                self.found_dead_code_or_error = True
            else:
                self.scan(module_string, filename=module)

        unique_imports = set(item.name for item in self.defined_imports)
        for import_name in unique_imports:
            path = os.path.join('whitelists', import_name) + '_whitelist.py'
            if exclude_file(path):
                self._log('Excluded whitelist:', path)
            else:
                try:
                    module_data = pkgutil.get_data('vulture', path)
                    self._log('Included whitelist:', path)
                except IOError:
                    # Most imported modules don't have a whitelist.
                    continue
                module_string = module_data.decode("utf-8")
                self.scan(module_string, filename=path)

    def get_unused_code(self, min_confidence=0, sort_by_size=False):
        """
        Return ordered list of unused Item objects.
        """
        if not 0 <= min_confidence <= 100:
            raise ValueError('min_confidence must be between 0 and 100.')

        def by_name(item):
            return (item.filename.lower(), item.first_lineno)

        def by_size(item):
            return (item.size,) + by_name(item)

        unused_code = (self.unused_attrs + self.unused_classes +
                       self.unused_funcs + self.unused_imports +
                       self.unused_props + self.unused_vars +
                       self.unreachable_code)

        confidently_unused = [obj for obj in unused_code
                              if obj.confidence >= min_confidence]

        return sorted(confidently_unused,
                      key=by_size if sort_by_size else by_name)

    def make_whitelist(self, min_confidence=0, sort_by_size=False):
        for item in self.get_unused_code(
                min_confidence=min_confidence, sort_by_size=sort_by_size):
            if item.typ != 'unreachable_code':
                prefix = '_.' if item.typ in ['attribute', 'property'] else ''
                print("{}{}  # unused {} ({}:{:d})".format(
                        prefix, item.name, item.typ,
                        utils.format_path(item.filename), item.first_lineno))
                self.found_dead_code_or_error = True
        return self.found_dead_code_or_error

    def report(self, min_confidence=0, sort_by_size=False):
        """
        Print ordered list of Item objects to stdout.
        """
        for item in self.get_unused_code(
                min_confidence=min_confidence, sort_by_size=sort_by_size):
            print(item.get_report(add_size=sort_by_size))
            self.found_dead_code_or_error = True
        return self.found_dead_code_or_error

    def _ignore_name(self, name):
        return any(fnmatchcase(name, pattern) for pattern in self.ignore_names)

    @property
    def unused_classes(self):
        return _get_unused_items(
            self.defined_classes,
            self.used_attrs | self.used_names)

    @property
    def unused_funcs(self):
        return _get_unused_items(
            self.defined_funcs,
            self.used_attrs | self.used_names)

    @property
    def unused_imports(self):
        return _get_unused_items(
            self.defined_imports,
            self.used_names | self.used_attrs)

    @property
    def unused_props(self):
        return _get_unused_items(self.defined_props, self.used_attrs)

    @property
    def unused_vars(self):
        return _get_unused_items(
            self.defined_vars,
            self.used_attrs | self.used_names)

    @property
    def unused_attrs(self):
        return _get_unused_items(self.defined_attrs, self.used_attrs)

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
            name = name_and_alias.name.partition('.')[0]
            alias = name_and_alias.asname
            self._define(
                self.defined_imports, alias or name, node,
                confidence=90, ignore=_ignore_import)
            if alias is not None:
                self.used_names.add(name_and_alias.name)

    def _handle_conditional_node(self, node, name):
        if utils.condition_is_always_false(node.test):
            self._define(
                self.unreachable_code, name, node,
                last_node=node.body[-1],
                message="unsatisfiable '{name}' condition".format(**locals()),
                confidence=100)
        else:
            else_body = getattr(node, 'orelse')
            if utils.condition_is_always_true(node.test) and else_body:
                self._define(
                    self.unreachable_code, 'else', else_body[0],
                    last_node=else_body[-1],
                    message="unreachable 'else' block",
                    confidence=100)

    def _define(self, collection, name, first_node, last_node=None,
                message='', confidence=DEFAULT_CONFIDENCE, ignore=None):
        last_node = last_node or first_node
        typ = collection.typ
        if (ignore and ignore(self.filename, name)) or self._ignore_name(name):
            self._log('Ignoring {typ} "{name}"'.format(**locals()))
        else:
            first_lineno = first_node.lineno
            last_lineno = lines.get_last_line_number(last_node)
            collection.append(
                Item(name, typ, self.filename, first_lineno, last_lineno,
                     message=message, confidence=confidence))

    def _define_variable(self, name, node, confidence=DEFAULT_CONFIDENCE):
        self._define(self.defined_vars, name, node, confidence=confidence,
                     ignore=_ignore_variable)

    def visit_arg(self, node):
        """Function argument.

        ast.arg was added in Python 3.0.
        ast.arg.lineno was added in Python 3.4.
        """
        self._define_variable(node.arg, node, confidence=100)

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Store):
            self._define(self.defined_attrs, node.attr, node)
        elif isinstance(node.ctx, ast.Load):
            self.used_attrs.add(node.attr)

    def visit_ClassDef(self, node):
        self._define(
            self.defined_classes, node.name, node, ignore=_ignore_class)

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if getattr(decorator, 'id', None) == 'property':
                self._define(self.defined_props, node.name, node)
                break
        else:
            # Function is not a property.
            self._define(
                self.defined_funcs, node.name, node,
                ignore=_ignore_function)

        # Detect *args and **kwargs parameters. Python 3 recognizes them
        # in visit_Name. For Python 2 we use this workaround. We can't
        # use visit_arguments, because its node has no lineno.
        for param in [node.args.vararg, node.args.kwarg]:
            if param and isinstance(param, str):
                self._define_variable(param, node, confidence=100)

    def visit_If(self, node):
        self._handle_conditional_node(node, 'if')

    def visit_Import(self, node):
        self._add_aliases(node)

    def visit_ImportFrom(self, node):
        if node.module != '__future__':
            self._add_aliases(node)

    def visit_Name(self, node):
        if (isinstance(node.ctx, ast.Load) and
                node.id not in IGNORED_VARIABLE_NAMES):
            self.used_names.add(node.id)
        elif isinstance(node.ctx, (ast.Param, ast.Store)):
            self._define_variable(node.id, node)

    def visit_Str(self, node):
        """
        Parse variable names in format strings:

        '%(my_var)s' % locals()
        '{my_var}'.format(**locals())

        """
        # Old format strings.
        self.used_names |= set(re.findall(r'\%\((\w+)\)', node.s))

        def is_identifier(s):
            return bool(re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', s))

        # New format strings.
        parser = string.Formatter()
        try:
            names = [name for _, name, _, _ in parser.parse(node.s) if name]
        except ValueError:
            # Invalid format string.
            names = []

        for field_name in names:
            # Remove brackets and contents: "a[0][b].c[d].e" -> "a.c.e".
            # "a.b.c" -> name = "a", attributes = ["b", "c"]
            name_and_attrs = re.sub(r'\[\w*\]', '', field_name).split('.')
            name = name_and_attrs[0]
            if is_identifier(name):
                self.used_names.add(name)
            for attr in name_and_attrs[1:]:
                if is_identifier(attr):
                    self.used_attrs.add(attr)

    def visit_While(self, node):
        self._handle_conditional_node(node, 'while')

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, None)
        if self.verbose:
            lineno = getattr(node, 'lineno', 1)
            line = self.code[lineno - 1] if self.code else ''
            self._log(lineno, ast.dump(node), line)
        if visitor:
            visitor(node)
        return self.generic_visit(node)

    def _handle_ast_list(self, ast_list):
        """
        Find unreachable nodes in the given sequence of ast nodes.
        """
        for index, node in enumerate(ast_list):
            if isinstance(node, (ast.Break, ast.Continue, ast.Raise,
                                 ast.Return)):
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
                    message="unreachable code after '{class_name}'".format(
                        **locals()),
                    confidence=100)
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


def _parse_args():
    def csv(exclude):
        return exclude.split(',')

    usage = "%(prog)s [options] PATH [PATH ...]"
    version = "vulture {0}".format(__version__)
    glob_help = 'Patterns may contain glob wildcards (*, ?, [abc], [!abc]).'
    parser = argparse.ArgumentParser(prog='vulture', usage=usage)
    parser.add_argument(
        'paths', nargs='+', metavar='PATH',
        help='Paths may be Python files or directories. For each directory'
        ' Vulture analyzes all contained *.py files.')
    parser.add_argument(
        '--exclude', metavar='PATTERNS', type=csv,
        help='Comma-separated list of paths to ignore (e.g.,'
        ' "*settings.py,docs/*.py"). {glob_help} A PATTERN without globbing'
        ' characters is treated as *PATTERN*.'.format(**locals()))
    parser.add_argument(
        '--ignore-names', metavar='PATTERNS', type=csv, default=None,
        help='Comma-separated list of names to ignore (e.g., "visit_*,do_*").'
        ' {glob_help}'.format(**locals()))
    parser.add_argument(
        '--make-whitelist', action='store_true',
        help='Report unused code in a format that can be added to a'
        ' whitelist module.')
    parser.add_argument(
        '--min-confidence', type=int, default=0,
        help='Minimum confidence (between 0 and 100) for code to be'
        ' reported as unused.')
    parser.add_argument(
        "--sort-by-size", action="store_true",
        help='Sort unused functions and classes by their lines of code.')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--version', action='version', version=version)
    return parser.parse_args()


def main():
    args = _parse_args()
    vulture = Vulture(verbose=args.verbose, ignore_names=args.ignore_names)
    vulture.scavenge(args.paths, exclude=args.exclude)
    report_func = (vulture.make_whitelist if args.make_whitelist
                   else vulture.report)
    sys.exit(report_func(
        min_confidence=args.min_confidence,
        sort_by_size=args.sort_by_size))
