#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# vulture - Find dead code.
#
# Copyright (c) 2012-2017 Jendrik Seipp (jendrikseipp@gmail.com)
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

import ast
from fnmatch import fnmatchcase
import optparse
import os
import pkgutil
import re
import string
import sys

from vulture import lines
from vulture import utils

__version__ = '0.23'

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
    name = os.path.basename(filename)
    return any(
        fnmatchcase(name, pattern)
        for pattern in ['test*.py', '*_test.py'])


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
    def __init__(self, name, typ, filename, lineno, size=1, message='',
                 confidence=DEFAULT_CONFIDENCE):
        self.name = name
        self.typ = typ
        self.filename = filename
        self.lineno = lineno
        self.size = size
        self.message = message or "unused {typ} '{name}'".format(**locals())
        self.confidence = confidence

    def _tuple(self):
        return (self.filename, self.lineno, self.name)

    def __repr__(self):
        return repr(self.name)

    def __eq__(self, other):
        return self._tuple() == other._tuple()

    def __hash__(self):
        return hash(self._tuple())


class Vulture(ast.NodeVisitor):
    """Find dead code."""
    def __init__(self, exclude=None, verbose=False, sort_by_size=False,
                 min_confidence=0):
        if not 0 <= min_confidence <= 100:
            raise ValueError('min_confidence must be between 0 and 100.')
        self.exclude = []
        self.sort_by_size = sort_by_size
        self.min_confidence = min_confidence

        for pattern in exclude or []:
            if not any(char in pattern for char in ['*', '?', '[']):
                pattern = '*{0}*'.format(pattern)
            self.exclude.append(pattern)

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
        else:
            self.visit(node)

    def _get_modules(self, paths, toplevel=True):
        """Take files from the command line even if they don't end with .py."""
        modules = []
        for path in paths:
            path = os.path.abspath(path)
            if toplevel and path.endswith('.pyc'):
                sys.exit('.pyc files are not supported: {0}'.format(path))
            if os.path.isfile(path) and (path.endswith('.py') or toplevel):
                modules.append(path)
            elif os.path.isdir(path):
                subpaths = [
                    os.path.join(path, filename)
                    for filename in sorted(os.listdir(path))]
                modules.extend(self._get_modules(subpaths, toplevel=False))
            elif toplevel:
                sys.exit('Error: {0} could not be found.'.format(path))
        return modules

    def scavenge(self, paths):
        def exclude(name):
            return any(fnmatchcase(name, pattern) for pattern in self.exclude)

        for module in self._get_modules(paths):
            if exclude(module):
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
            path = os.path.join('whitelists', import_name) + '.py'
            if exclude(path):
                self._log('Excluded whitelist:', path)
            else:
                try:
                    module_data = pkgutil.get_data('vulture', path)
                    self._log('Included whitelist:', path)
                except IOError:
                    # Most imported modules don't have a whitelist.
                    continue
                if module_data is None:
                    sys.exit('Error: Please use "python -m vulture".')
                module_string = module_data.decode("utf-8")
                self.scan(module_string, filename=path)

    def get_unused_code(self):
        """
        Return ordered list of unused Item objects.
        """
        def by_size(item):
            return item.size

        def by_name(item):
            return (item.filename.lower(), item.lineno)

        unused_code = (self.unused_attrs + self.unused_classes +
                       self.unused_funcs + self.unused_imports +
                       self.unused_props + self.unused_vars +
                       self.unreachable_code)

        confidently_unused = [obj for obj in unused_code
                              if obj.confidence >= self.min_confidence]

        return sorted(confidently_unused,
                      key=by_size if self.sort_by_size else by_name)

    def report(self):
        """
        Print ordered list of Item objects to stdout.
        """
        for item in self.get_unused_code():
            if self.sort_by_size:
                line_format = 'line' if item.size == 1 else 'lines'
                size_report = ', {0:d} {1}'.format(item.size, line_format)
            else:
                size_report = ''

            print("{0}:{1:d}: {2} ({3}% confidence{4})".format(
                utils.format_path(item.filename), item.lineno,
                item.message, item.confidence, size_report))
            self.found_dead_code_or_error = True
        return self.found_dead_code_or_error

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
        assert isinstance(node, (ast.Import, ast.ImportFrom))
        for name_and_alias in node.names:
            # Store only top-level module name ("os.path" -> "os").
            # We can't detect when "os.path" is used.
            name = name_and_alias.name.partition('.')[0]
            alias = name_and_alias.asname
            self._define(
                self.defined_imports, alias or name, node.lineno,
                confidence=90, ignore=_ignore_import)
            if alias is not None:
                self.used_names.add(name_and_alias.name)

    def _define(self, collection, name, lineno, size=1, message='',
                confidence=DEFAULT_CONFIDENCE, ignore=None):
        typ = collection.typ
        if ignore and ignore(self.filename, name):
            self._log('Ignoring {typ} "{name}"'.format(**locals()))
        else:
            collection.append(
                Item(name, typ, self.filename, lineno, size=size,
                     message=message, confidence=confidence))

    def _define_variable(self, name, lineno, confidence=DEFAULT_CONFIDENCE):
        self._define(self.defined_vars, name, lineno, confidence=confidence,
                     ignore=_ignore_variable)

    def visit_alias(self, node):
        """
        Use the methods below for imports to have access to line numbers
        and to filter imports from __future__.
        """
        pass

    def visit_arg(self, node):
        """Function argument. Python 3 only. Has lineno since Python 3.4"""
        self._define_variable(node.arg, getattr(node, 'lineno', -1),
                              confidence=100)

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Store):
            size = lines.count_lines(node) if self.sort_by_size else 1
            self._define(self.defined_attrs, node.attr, node.lineno, size=size)
        elif isinstance(node.ctx, ast.Load):
            self.used_attrs.add(node.attr)

    def visit_ClassDef(self, node):
        size = lines.count_lines(node) if self.sort_by_size else 1
        self._define(
            self.defined_classes, node.name, node.lineno,
            size=size, ignore=_ignore_class)

    def visit_FunctionDef(self, node):
        size = lines.count_lines(node) if self.sort_by_size else 1
        for decorator in node.decorator_list:
            if getattr(decorator, 'id', None) == 'property':
                self._define(
                    self.defined_props, node.name, node.lineno, size=size)
                break
        else:
            # Function is not a property.
            self._define(
                self.defined_funcs, node.name, node.lineno, size=size,
                ignore=_ignore_function)

        # Detect *args and **kwargs parameters. Python 3 recognizes them
        # in visit_Name. For Python 2 we use this workaround. We can't
        # use visit_arguments, because its node has no lineno.
        for param in [node.args.vararg, node.args.kwarg]:
            if param and isinstance(param, str):
                self._define_variable(param, node.lineno, confidence=100)

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
            self._define_variable(node.id, node.lineno)

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
                    first_unreachable_node.lineno,
                    size=lines.get_last_line_number(ast_list[-1]) -
                    first_unreachable_node.lineno + 1,
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
    def csv(option, _, value, parser):
        setattr(parser.values, option.dest, value.split(','))
    usage = """\
usage: %prog [options] PATH [PATH ...]

Paths may be Python files or directories. For each directory vulture
analyzes all contained *.py files.
"""
    version = "vulture {0}".format(__version__)
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option(
        '--exclude', action='callback', callback=csv, metavar='PATTERN',
        type='string', default=[],
        help=(
            'Comma-separated list of paths to ignore (e.g.,'
            ' *settings.py,docs/*.py). PATTERNs can contain globbing'
            ' characters (*, ?, [, ]). Treat PATTERNs without globbing'
            ' characters as *PATTERN*.'))
    parser.add_option(
        "--sort-by-size", action="store_true",
        help="Sort unused functions and classes by their lines of code")
    parser.add_option('-v', '--verbose', action='store_true')
    parser.add_option(
        '--min-confidence', action='store', type='int', default=0, help=(
            'Minimum confidence (between 0 and 100) for code to be'
            ' reported as unused.'))
    options, args = parser.parse_args()
    return options, args


def main():
    options, args = _parse_args()
    vulture = Vulture(exclude=options.exclude, verbose=options.verbose,
                      sort_by_size=options.sort_by_size,
                      min_confidence=options.min_confidence)
    vulture.scavenge(args)
    sys.exit(vulture.report())


# Only useful for Python 2.6 which doesn't support "python -m vulture".
if __name__ == '__main__':
    main()
