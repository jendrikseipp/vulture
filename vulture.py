#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# vulture - Find dead code.
#
# Copyright (C) 2012-2015  Jendrik Seipp (jendrikseipp@web.de)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import ast
from fnmatch import fnmatchcase
import optparse
import os
import re
import sys

__version__ = '0.7'

# Parse variable names in template strings.
FORMAT_STRING_PATTERNS = [re.compile(r'\%\((\w+)\)'), re.compile(r'{(\w+)}')]


def _ignore_function(name):
    return ((name.startswith('__') and name.endswith('__')) or
            name.startswith('test_'))


class Item(str):
    def __new__(cls, name, typ, file, lineno):
        item = str.__new__(cls, name)
        item.typ = typ
        item.file = file
        item.lineno = lineno
        return item


class Vulture(ast.NodeVisitor):
    """Find dead stuff."""
    def __init__(self, exclude=None, verbose=False):
        self.exclude = []
        for pattern in exclude or []:
            if not any(char in pattern for char in ['*', '?', '[']):
                pattern = '*%s*' % pattern
            self.exclude.append(pattern)

        self.verbose = verbose

        self.defined_funcs = []
        self.used_funcs = []
        self.defined_props = []
        self.defined_attrs = []
        self.used_attrs = []
        self.defined_vars = []
        self.used_vars = []
        self.tuple_assign_vars = []

        self.file = ''
        self.code = None

    def scan(self, node_string):
        self.code = node_string.splitlines()
        node = ast.parse(node_string, filename=self.file)
        self.visit(node)

    def _get_modules(self, paths, toplevel=True):
        """Take files from the command line even if they don't end with .py."""
        modules = []
        for path in paths:
            path = os.path.abspath(path)
            if os.path.isfile(path) and (path.endswith('.py') or toplevel):
                modules.append(path)
            elif os.path.isdir(path):
                subpaths = [os.path.join(path, filename)
                            for filename in sorted(os.listdir(path))]
                modules.extend(self._get_modules(subpaths, toplevel=False))
            elif toplevel:
                sys.exit('Error: %s could not be found.' % path)
        return modules

    def scavenge(self, paths):
        modules = self._get_modules(paths)
        included_modules = []
        for module in modules:
            if any(fnmatchcase(module, pattern) for pattern in self.exclude):
                self.log('Excluded:', module)
            else:
                included_modules.append(module)

        for module in included_modules:
            self.log('Scanning:', module)
            with open(module) as f:
                module_string = f.read()
            self.file = module
            self.scan(module_string)

    def report(self):
        def file_lineno(item):
            return (item.file.lower(), item.lineno)
        unused_item_found = False
        for item in sorted(self.unused_funcs + self.unused_props +
                           self.unused_vars + self.unused_attrs,
                           key=file_lineno):
            relpath = os.path.relpath(item.file)
            path = relpath if not relpath.startswith('..') else item.file
            print("%s:%d: Unused %s '%s'" % (path, item.lineno, item.typ,
                                             item))
            unused_item_found = True
        return unused_item_found

    def get_unused(self, defined, used):
        return list(sorted(set(defined) - set(used), key=lambda x: x.lower()))

    @property
    def unused_funcs(self):
        return self.get_unused(self.defined_funcs,
                               self.used_funcs + self.used_attrs)

    @property
    def unused_props(self):
        return self.get_unused(self.defined_props, self.used_attrs)

    @property
    def unused_vars(self):
        return self.get_unused(
            self.defined_vars,
            self.used_vars + self.used_attrs + self.tuple_assign_vars)

    @property
    def unused_attrs(self):
        return self.get_unused(self.defined_attrs, self.used_attrs)

    def _get_lineno(self, node):
        return getattr(node, 'lineno', 1)

    def _get_line(self, node):
        return self.code[self._get_lineno(node) - 1] if self.code else ''

    def _get_item(self, node, typ):
        name = getattr(node, 'name', None)
        id = getattr(node, 'id', None)
        attr = getattr(node, 'attr', None)
        assert len([x for x in (name, id, attr) if x is not None]) == 1
        return Item(name or id or attr, typ, self.file, node.lineno)

    def log(self, *args):
        if self.verbose:
            print(*args)

    def print_node(self, node):
        # Only create the strings, if we'll also print them.
        if self.verbose:
            self.log(
                self._get_lineno(node), ast.dump(node), self._get_line(node))

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if getattr(decorator, 'id', None) == 'property':
                self.defined_props.append(self._get_item(node, 'property'))
                break
        else:
            # Function is not a property.
            if not _ignore_function(node.name):
                self.defined_funcs.append(self._get_item(node, 'function'))

    def visit_Attribute(self, node):
        item = self._get_item(node, 'attribute')
        if isinstance(node.ctx, ast.Store):
            self.log('defined_attrs <-', item)
            self.defined_attrs.append(item)
        elif isinstance(node.ctx, ast.Load):
            self.log('used_attrs <-', item)
            self.used_attrs.append(item)

    def visit_Name(self, node):
        if node.id != 'object':
            self.used_funcs.append(node.id)
            if isinstance(node.ctx, ast.Load):
                self.log('used_vars <-', node.id)
                self.used_vars.append(node.id)
            elif isinstance(node.ctx, ast.Store):
                # Ignore _x (pylint convention), __x, __x__ (special method).
                if not node.id.startswith('_'):
                    item = self._get_item(node, 'variable')
                    self.log('defined_vars <-', item)
                    self.defined_vars.append(item)

    def _find_tuple_assigns(self, node):
        # Find all tuple assignments. Those have the form
        # Assign->Tuple->Name or For->Tuple->Name or comprehension->Tuple->Name
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, ast.Tuple):
                continue
            for grandchild in ast.walk(child):
                if (isinstance(grandchild, ast.Name) and
                        isinstance(grandchild.ctx, ast.Store)):
                        self.log('tuple_assign_vars <-', grandchild.id)
                        self.tuple_assign_vars.append(grandchild.id)

    def visit_Assign(self, node):
        self._find_tuple_assigns(node)

    def visit_For(self, node):
        self._find_tuple_assigns(node)

    def visit_comprehension(self, node):
        self._find_tuple_assigns(node)

    def visit_ClassDef(self, node):
        self.defined_funcs.append(self._get_item(node, 'class'))

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
        if visitor is not None:
            self.print_node(node)
            visitor(node)
        return self.generic_visit(node)


def parse_args():
    def csv(option, opt, value, parser):
        setattr(parser.values, option.dest, value.split(','))
    usage = 'usage: %prog [options] PATH [PATH ...]'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--exclude', action='callback', callback=csv,
                      type='string', default=[],
                      help='Comma-separated list of filename patterns to '
                           'exclude (e.g. svn,external).')
    parser.add_option('-v', '--verbose', action='store_true')
    options, args = parser.parse_args()
    return options, args


def main():
    options, args = parse_args()
    vulture = Vulture(exclude=options.exclude, verbose=options.verbose)
    vulture.scavenge(args)
    sys.exit(vulture.report())


if __name__ == '__main__':
    main()
