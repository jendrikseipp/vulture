"""

Vulture sometimes reports used code as unused. To avoid these
false-positives, you can write a Python file that explicitly uses the
code and pass it to vulture:

vulture myscript.py mydir mywhitelist.py

This file explicitly uses code from the Python standard library that is
often incorrectly detected as unused.

"""

import ast
import collections
import sys


# NodeVisitor methods are called implicitly.
class WhitelistNodeVisitor(ast.NodeVisitor):
    def __getattr__(self, _):
        pass


whitelist_node_visitor = WhitelistNodeVisitor()

# TODO: Add missing methods.
whitelist_node_visitor.visit_arg
whitelist_node_visitor.visit_alias
whitelist_node_visitor.visit_Assign
whitelist_node_visitor.visit_Attribute
whitelist_node_visitor.visit_ClassDef
whitelist_node_visitor.visit_comprehension
whitelist_node_visitor.visit_For
whitelist_node_visitor.visit_FunctionDef
whitelist_node_visitor.visit_Import
whitelist_node_visitor.visit_ImportFrom
whitelist_node_visitor.visit_Name
whitelist_node_visitor.visit_Str


# To free memory, the "default_factory" attribute can be set to None.
collections.defaultdict(list).default_factory = None
collections.defaultdict(list).default_factory


# Never report redirected streams as unused.
sys.stderr
sys.stdin
sys.stdout
