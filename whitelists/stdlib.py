"""

Vulture sometimes reports used code as unused. To avoid these
false-positives, you can write a Python file that explicitly uses the
code and pass it to vulture:

vulture myscript.py mydir mywhitelist.py

When creating a whitelist file, you have to make sure not to write code
that hides unused code in other files. E.g., this is why we don't import
and access the "sys" module below. If we did import it, vulture would
not be able to detect whether other files import "sys" without using it.

This file explicitly uses code from the Python standard library that is
often incorrectly detected as unused.

"""


class Whitelist:
    """
    Helper class that allows mocking Python objects.

    Use it to create whitelist files that are not only syntactically
    correct, but can also be executed.

    """
    def __getattr__(self, _):
        pass


# NodeVisitor methods are called implicitly.
# TODO: Add missing methods.
whitelist_node_visitor = Whitelist()
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
whitelist_defaultdict = Whitelist()
whitelist_defaultdict.default_factory

# Never report redirected streams as unused.
whitelist_sys = Whitelist()
whitelist_sys.stderr
whitelist_sys.stdin
whitelist_sys.stdout
