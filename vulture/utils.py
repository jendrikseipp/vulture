# -*- coding: utf-8 -*-
#
# vulture - Find dead code.
#
# Copyright (c) 2012-2020 Jendrik Seipp (jendrikseipp@gmail.com)
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

import ast
import codecs
import os
import re
import sys
import tokenize

# Encoding to use when converting input files to unicode. Python 2 trips
# over the BOM, so we use "utf-8-sig" which drops the BOM.
ENCODING = "utf-8-sig"

# The ast module in Python 2 trips over "coding" cookies, so strip them.
ENCODING_REGEX = re.compile(
    r"^[ \t\v]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+).*?$", flags=re.M
)


class VultureInputException(Exception):
    pass


def _safe_eval(node, default):
    """
    Safely evaluate the Boolean expression under the given AST node.

    Substitute `default` for all sub-expressions that cannot be
    evaluated (because variables or functions are undefined).

    We could use eval() to evaluate more sub-expressions. However, this
    function is not safe for arbitrary Python code. Even after
    overwriting the "__builtins__" dictionary, the original dictionary
    can be restored
    (https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html).

    """
    if isinstance(node, ast.BoolOp):
        results = [_safe_eval(value, default) for value in node.values]
        if isinstance(node.op, ast.And):
            return all(results)
        else:
            return any(results)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not _safe_eval(node.operand, not default)
    else:
        try:
            return ast.literal_eval(node)
        except ValueError:
            return default


def condition_is_always_false(condition):
    return not _safe_eval(condition, True)


def condition_is_always_true(condition):
    return _safe_eval(condition, False)


def format_path(path):
    if not path:
        return path
    relpath = os.path.relpath(path)
    return relpath if not relpath.startswith("..") else path


def get_decorator_name(decorator):
    if isinstance(decorator, ast.Call):
        decorator = decorator.func
    parts = []
    while isinstance(decorator, ast.Attribute):
        parts.append(decorator.attr)
        decorator = decorator.value
    parts.append(decorator.id)
    return "@" + ".".join(reversed(parts))


def get_modules(paths, toplevel=True):
    """Take files from the command line even if they don't end with .py."""
    modules = []
    for path in paths:
        path = os.path.abspath(path)
        if toplevel and path.endswith(".pyc"):
            sys.exit(".pyc files are not supported: {}".format(path))
        if os.path.isfile(path) and (path.endswith(".py") or toplevel):
            modules.append(path)
        elif os.path.isdir(path):
            subpaths = [
                os.path.join(path, filename)
                for filename in sorted(os.listdir(path))
            ]
            modules.extend(get_modules(subpaths, toplevel=False))
        elif toplevel:
            sys.exit("Error: {} could not be found.".format(path))
    return modules


def read_file(filename):
    # Python >= 3.2
    try:
        # Use encoding detected by tokenize.detect_encoding().
        with tokenize.open(filename) as f:
            return f.read()
    except (SyntaxError, UnicodeDecodeError) as err:
        raise VultureInputException(err)
    except AttributeError:
        # tokenize.open was added in Python 3.2.
        pass

    # Python < 3.2
    try:
        with codecs.open(filename, encoding=ENCODING) as f:
            return f.read()
    except UnicodeDecodeError as err:
        raise VultureInputException(err)


def sanitize_code(code):
    return ENCODING_REGEX.sub("", code, count=1)


class LoggingList(list):
    def __init__(self, typ, verbose):
        self.typ = typ
        self._verbose = verbose
        return list.__init__(self)

    def append(self, item):
        if self._verbose:
            print('define {} "{}"'.format(self.typ, item.name))
        list.append(self, item)


class LoggingSet(set):
    def __init__(self, typ, verbose):
        self.typ = typ
        self._verbose = verbose
        return set.__init__(self)

    def add(self, name):
        if self._verbose:
            print('use {} "{}"'.format(self.typ, name))
        set.add(self, name)
