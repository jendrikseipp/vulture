# -*- coding: utf-8 -*-
#
# vulture - Find dead code.
#
# Copyright (C) 2012  Jendrik Seipp (jendrikseipp@web.de)
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

import ast
from fnmatch import fnmatchcase
import os
import re


FORMAT_STRING_PATTERN = re.compile(r'\%\((\S+)\)s')


class Item(str):
    def __new__(cls, name, typ, file, lineno, line):
        item = str.__new__(cls, name)
        item.typ = typ
        item.file = file
        item.lineno = lineno
        item.line = line
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

        self.file = None
        self.code = None

    def scavenge(self, paths):
        modules = self.get_modules(paths)
        included_modules = []
        for module in modules:
            if any(fnmatchcase(module, pattern) for pattern in self.exclude):
                self.log('Excluded:', module)
                continue
            included_modules.append(module)

        for module in included_modules:
            self.log('Scanning:', module)
            module_string = open(module).read()
            self.file = module
            self.scan(module_string)

    def report(self):
        def sort_by_file(item):
            return item.file.lower()
        for item in sorted(self.unused_funcs + self.unused_props +
                           self.unused_vars, key=sort_by_file):
            relpath = os.path.relpath(item.file)
            path = relpath if not relpath.startswith('..') else item.file
            print "%s:%d: Unused %s '%s'" % (path, item.lineno, item.typ, item)

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
        return self.get_unused(self.defined_vars,
                    self.used_vars + self.used_attrs + self.tuple_assign_vars)

    @property
    def unused_attrs(self):
        return self.get_unused(self.defined_attrs, self.used_attrs)

    def _get_line(self, node):
        lineno = getattr(node, 'lineno', 1)
        return self.code[lineno - 1] if self.code else ""

    def _get_item(self, node, typ):
        name = getattr(node, 'name', None)
        id = getattr(node, 'id', None)
        attr = getattr(node, 'attr', None)
        assert len([x for x in (name, id, attr) if x is not None]) == 1
        return Item(name or id or attr, typ, self.file, node.lineno,
                    self._get_line(node))

    def log(self, *args):
        if not self.verbose:
            return
        for arg in args:
            print arg,
        print

    def print_node(self, node):
        self.log(node.lineno, ast.dump(node), self._get_line(node))

    def get_modules(self, paths):
        modules = []
        for path in paths:
            path = os.path.abspath(path)
            if os.path.isfile(path) and path.endswith('.py'):
                modules.append(path)
            elif os.path.isdir(path):
                subpaths = [os.path.join(path, filename)
                            for filename in sorted(os.listdir(path))]
                modules.extend(self.get_modules(subpaths))
        return modules

    def _get_func_name(self, func):
        for field in func._fields:
            if field == 'id':
                return func.id
            elif field == 'func':
                return self._get_func_name(func.func)
        return func.attr

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if getattr(decorator, 'id', None) == 'property':
                self.defined_props.append(self._get_item(node, 'property'))
                break
        else:
            # Only executed if function is not a property.
            if not (node.name.startswith('__') and node.name.endswith('__')):
                self.defined_funcs.append(self._get_item(node, 'function'))

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined_attrs.append(self._get_item(node, 'attribute'))
        elif isinstance(node.ctx, ast.Load):
            self.used_attrs.append(node.attr)

    def visit_Name(self, node):
        if node.id != 'object':
            self.used_funcs.append(node.id)
            if isinstance(node.ctx, ast.Load):
                self.used_vars.append(node.id)
            elif isinstance(node.ctx, ast.Store):
                if not (node.id.startswith('__') and node.id.endswith('__')):
                    self.defined_vars.append(self._get_item(node, 'variable'))

    def _find_tuple_assigns(self, node):
        # Find all tuple assignments. Those have the form
        # Assign->Tuple->Name or For->Tuple->Name
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, ast.Tuple):
                continue
            for grandchild in ast.walk(child):
                if (isinstance(grandchild, ast.Name) and
                    isinstance(grandchild.ctx, ast.Store)):
                    self.tuple_assign_vars.append(grandchild.id)

    def visit_Assign(self, node):
        self._find_tuple_assigns(node)

    def visit_For(self, node):
        self._find_tuple_assigns(node)

    def visit_ClassDef(self, node):
        self.defined_funcs.append(self._get_item(node, 'class'))

    def visit_Str(self, node):
        """Variables may appear in format strings: '%(a)s' % locals()"""
        self.used_vars.extend(FORMAT_STRING_PATTERN.findall(node.s))

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, None)
        if visitor is not None:
            self.print_node(node)
            visitor(node)
        return self.generic_visit(node)

    def scan(self, node_string):
        self.code = node_string.splitlines()
        node = ast.parse(node_string)
        self.visit(node)
