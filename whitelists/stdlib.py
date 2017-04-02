"""

Vulture sometimes reports used code as unused. To avoid these
false-positives, you can write a Python file that explicitly uses the
code and pass it to vulture:

vulture myscript.py mydir mywhitelist.py

This file explicitly uses code from the Python standard library that is
often incorrectly detected as unused.

"""

from ast import NodeVisitor
import collections

# NodeVisitor methods are called implicitly.
class WhitelistNodeVisitor(NodeVisitor):
    def visit_arg(self, node):
        node
        pass

    def visit_alias(self, node):
        pass

    def visit_Assign(self, node):
        pass

    def visit_Attribute(self, node):
        pass

    def visit_ClassDef(self, node):
        pass

    def visit_comprehension(self, node):
        pass

    def visit_For(self, node):
        pass

    def visit_FunctionDef(self, node):
        pass

    def visit_Import(self, node):
        pass

    def visit_ImportFrom(self, node):
        pass

    def visit_Name(self, node):
        pass

    def visit_Str(self, node):
        pass

WhitelistNodeVisitor.visit_arg
WhitelistNodeVisitor.visit_alias
WhitelistNodeVisitor.visit_Assign
WhitelistNodeVisitor.visit_Attribute
WhitelistNodeVisitor.visit_ClassDef
WhitelistNodeVisitor.visit_comprehension
WhitelistNodeVisitor.visit_For
WhitelistNodeVisitor.visit_FunctionDef
WhitelistNodeVisitor.visit_Import
WhitelistNodeVisitor.visit_ImportFrom
WhitelistNodeVisitor.visit_Name
WhitelistNodeVisitor.visit_Str


# To free memory, the "default_factory" attribute can be set to None.
collections.defaultdict(list).default_factory = None
collections.defaultdict(list).default_factory
