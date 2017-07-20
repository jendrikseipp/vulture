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
import sys

from vulture import lines
from vulture import utils

__version__ = '0.19'

# The ast module in Python 2 trips over "coding" cookies, so strip them.
ENCODING_REGEX = re.compile(
    r"^[ \t\v]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+).*?$", flags=re.M)

# Parse variable names in template strings.
FORMAT_STRING_PATTERNS = [re.compile(r'\%\((\w+)\)'), re.compile(r'{(\w+)}')]

IGNORED_VARIABLE_NAMES = ['object', 'self']
# True and False are NameConstants since Python 3.4.
if sys.version_info < (3, 4):
    IGNORED_VARIABLE_NAMES += ['True', 'False']

# Ignore star-imported names, since we cannot detect whether they are used.
IGNORED_IMPORTS = ["*"]


def _get_unused_items(defined, used):
    return list(sorted(set(defined) - set(used), key=lambda x: x.lower()))


def _is_special_name(name):
    return name.startswith('__') and name.endswith('__')


def _is_test_file(filename):
    name = os.path.basename(filename)
    return any(
        fnmatchcase(name, pattern)
        for pattern in ['test_*.py', '*_test.py'])


def _ignore_class(filename, class_name):
        return _is_test_file(filename) and class_name.startswith('Test')


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


class Item(str):
    def __new__(cls, name, typ, filename, lineno, size=1):
        item = str.__new__(cls, name)
        item.typ = typ
        item.filename = filename
        item.lineno = lineno
        item.size = size
        return item


class Vulture(ast.NodeVisitor):
    """Find dead code."""
    def __init__(self, exclude=None, verbose=False, sort_by_size=False):
        self.exclude = []
        self.sort_by_size = sort_by_size
        for pattern in exclude or []:
            if not any(char in pattern for char in ['*', '?', '[']):
                pattern = '*%s*' % pattern
            self.exclude.append(pattern)

        self.verbose = verbose

        def get_list(name):
            return utils.LoggingList(name, self.verbose)

        self.defined_attrs = get_list('defined_attrs')
        self.defined_classes = get_list('defined_classes')
        self.defined_funcs = get_list('defined_funcs')
        self.defined_imports = get_list('defined_imports')
        self.defined_props = get_list('defined_props')
        self.defined_vars = get_list('defined_vars')
        self.used_attrs = get_list('used_attrs')
        self.used_vars = get_list('used_vars')
        self.tuple_assign_vars = get_list('tuple_assign_vars')
        self.names_imported_as_aliases = get_list('names_imported_as_aliases')

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
            print('%s:%d: %s at "%s"' % (
                utils.format_path(filename), err.lineno,
                err.msg, err.text.strip()), file=sys.stderr)
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
                sys.exit('Error: %s could not be found.' % path)
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

        for name in self.defined_imports:
            path = os.path.join('whitelists', name) + '.py'
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

        return sorted(
            self.unused_attrs + self.unused_classes + self.unused_funcs +
            self.unused_imports + self.unused_props + self.unused_vars,
            key=by_size if self.sort_by_size else by_name)

    def report(self):
        """
        Print ordered list of Item objects to stdout.
        """
        for item in self.get_unused_code():
            line_format = 'line' if item.size == 1 else 'lines'
            size_report = (' (%d %s)' % (item.size, line_format)
                           if self.sort_by_size else '')
            print("%s:%d: Unused %s '%s'%s" % (
                utils.format_path(item.filename), item.lineno, item.typ,
                item, size_report))
            self.found_dead_code_or_error = True
        return self.found_dead_code_or_error

    @property
    def unused_classes(self):
        return _get_unused_items(
            self.defined_classes,
            self.used_attrs + self.used_vars + self.names_imported_as_aliases)

    @property
    def unused_funcs(self):
        return _get_unused_items(
            self.defined_funcs,
            self.used_attrs + self.used_vars + self.names_imported_as_aliases)

    @property
    def unused_imports(self):
        return _get_unused_items(
            self.defined_imports,
            self.used_vars + self.used_attrs + IGNORED_IMPORTS)

    @property
    def unused_props(self):
        return _get_unused_items(self.defined_props, self.used_attrs)

    @property
    def unused_vars(self):
        return _get_unused_items(
            self.defined_vars,
            self.used_attrs + self.used_vars + self.tuple_assign_vars +
            self.names_imported_as_aliases)

    @property
    def unused_attrs(self):
        return _get_unused_items(
            self.defined_attrs,
            self.used_attrs + self.used_vars)

    def _get_lineno(self, node):
        return getattr(node, 'lineno', 1)

    def _get_line(self, node):
        return self.code[self._get_lineno(node) - 1] if self.code else ''

    def _get_item(self, node, typ):
        """
        Return a lighter representation of the ast node ``node`` for
        later reporting purposes.
        """
        name = getattr(node, 'name', None)
        id_ = getattr(node, 'id', None)
        attr = getattr(node, 'attr', None)
        assert bool(name) ^ bool(id_) ^ bool(attr), (typ, dir(node))
        size = lines.count_lines(node) if self.sort_by_size else 1
        label = name or id_ or attr
        return Item(label, typ, self.filename, node.lineno, size)

    def _log(self, *args):
        if self.verbose:
            print(*args)

    def _print_node(self, node):
        # Only create the strings if we'll also print them.
        if self.verbose:
            self._log(
                self._get_lineno(node), ast.dump(node), self._get_line(node))

    def _add_aliases(self, node):
        assert isinstance(node, (ast.Import, ast.ImportFrom))
        for name_and_alias in node.names:
            # Store only top-level module name ("os.path" -> "os").
            # We can't detect when "os.path" is used.
            name = name_and_alias.name.partition('.')[0]
            alias = name_and_alias.asname
            self.defined_imports.append(
                Item(alias or name, 'import', self.filename, node.lineno))
            if alias is not None:
                self.names_imported_as_aliases.append(name_and_alias.name)

    def _define_variable(self, name, lineno):
        if _ignore_variable(self.filename, name):
            self._log('Ignoring variable {0} due to its name'.format(name))
        else:
            self.defined_vars.append(
                Item(name, 'variable', self.filename, lineno))

    def _find_tuple_assigns(self, node):
        # Find all tuple assignments. Those have the form
        # Assign->Tuple->Name or For->Tuple->Name or comprehension->Tuple->Name
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, ast.Tuple):
                continue
            for grandchild in ast.walk(child):
                if (isinstance(grandchild, ast.Name) and
                        isinstance(grandchild.ctx, ast.Store)):
                    self.tuple_assign_vars.append(grandchild.id)

    def visit_alias(self, node):
        """
        Use the methods below for imports to have access to line numbers
        and to filter imports from __future__.
        """
        pass

    def visit_arg(self, node):
        """Function argument. Python 3 only. Has lineno since Python 3.4"""
        self._define_variable(node.arg, getattr(node, 'lineno', -1))

    def visit_Assign(self, node):
        self._find_tuple_assigns(node)

    def visit_Attribute(self, node):
        item = self._get_item(node, 'attribute')
        if isinstance(node.ctx, ast.Store):
            self.defined_attrs.append(item)
        elif isinstance(node.ctx, ast.Load):
            self.used_attrs.append(node.attr)

    def visit_ClassDef(self, node):
        if _ignore_class(self.filename, node.name):
            self._log('Ignoring class {0} due to its name'.format(node.name))
        else:
            self.defined_classes.append(self._get_item(node, 'class'))

    def visit_comprehension(self, node):
        self._find_tuple_assigns(node)

    def visit_For(self, node):
        self._find_tuple_assigns(node)

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if getattr(decorator, 'id', None) == 'property':
                self.defined_props.append(self._get_item(node, 'property'))
                break
        else:
            # Function is not a property.
            if _ignore_function(self.filename, node.name):
                self._log(
                    'Ignoring function {0} due to its name'.format(node.name))
            else:
                self.defined_funcs.append(self._get_item(node, 'function'))

        # Detect *args and **kwargs parameters. Python 3 recognizes them
        # in visit_Name. For Python 2 we use this workaround. We can't
        # use visit_arguments, because its node has no lineno.
        for param in [node.args.vararg, node.args.kwarg]:
            if param and isinstance(param, str):
                self._define_variable(param, node.lineno)

    def visit_Import(self, node):
        self._add_aliases(node)

    def visit_ImportFrom(self, node):
        if node.module != '__future__':
            self._add_aliases(node)

    def visit_Name(self, node):
        if (isinstance(node.ctx, ast.Load) and
                node.id not in IGNORED_VARIABLE_NAMES):
            self.used_vars.append(node.id)
        elif isinstance(node.ctx, (ast.Param, ast.Store)):
            self._define_variable(node.id, node.lineno)

    def visit_Str(self, node):
        """
        Variables may appear in format strings:

        '%(my_var)s' % locals()
        '{my_var}'.format(**locals())

        """
        for pattern in FORMAT_STRING_PATTERNS:
            self.used_vars.extend(pattern.findall(node.s))

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, None)
        self._print_node(node)
        if visitor:
            visitor(node)
        else:
            self._log('Unhandled')
        return self.generic_visit(node)


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
        '--exclude', action='callback', callback=csv,
        type='string', default=[],
        help='Comma-separated list of paths to ignore (e.g. .svn,external)')
    parser.add_option(
        "--sort-by-size", action="store_true",
        help="Sort unused functions and classes by their lines of code")
    parser.add_option('-v', '--verbose', action='store_true')
    options, args = parser.parse_args()
    return options, args


def main():
    options, args = _parse_args()
    vulture = Vulture(exclude=options.exclude, verbose=options.verbose,
                      sort_by_size=options.sort_by_size)
    vulture.scavenge(args)
    sys.exit(vulture.report())


# Only useful for Python 2.6 which doesn't support "python -m vulture".
if __name__ == '__main__':
    main()
