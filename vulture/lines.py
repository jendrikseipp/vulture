import ast
import sys


def _get_last_child_with_lineno(node):
    """
    Return the last direct child of `node` that has a lineno attribute,
    or None if `node` has no such children.

    Almost all node._field lists are sorted by the order in which they
    appear in source code. For some nodes however, we have to skip some
    fields that either don't have line numbers (e.g., "ctx" and "names")
    or that are in the wrong position (e.g., "decorator_list" and
    "returns"). Then we choose the first field (i.e., the field with the
    highest line number) that actually contains a node. If it contains a
    list of nodes, we return the last one.

    """
    ignored_fields = {"ctx", "decorator_list", "names", "returns"}
    fields = node._fields
    # The fields of ast.Call are in the wrong order.
    if isinstance(node, ast.Call):
        fields = ("func", "args", "starargs", "keywords", "kwargs")
    for name in reversed(fields):
        if name in ignored_fields:
            continue

        try:
            last_field = getattr(node, name)
        except AttributeError:
            continue

        # Ignore non-AST objects like "is_async", "level" and "nl".
        if isinstance(last_field, ast.AST):
            return last_field
        elif isinstance(last_field, list) and last_field:
            return last_field[-1]
    return None


def get_last_line_number(node):
    """Estimate last line number of the given AST node.

    The estimate is based on the line number of the last descendant of
    `node` that has a lineno attribute. Therefore, it underestimates the
    size of code ending with, e.g., multiline strings and comments.

    When traversing the tree, we may see a mix of nodes with line
    numbers and nodes without line numbers. We therefore, store the
    maximum line number seen so far and report it at the end. A more
    accurate (but also slower to compute) estimate would traverse all
    children, instead of just the last one, since choosing the last one
    may lead to a path that ends with a node without line number.

    """
    max_lineno = node.lineno
    while True:
        last_child = _get_last_child_with_lineno(node)
        if last_child is None:
            return max_lineno
        else:
            try:
                max_lineno = max(max_lineno, last_child.lineno)
            except AttributeError:
                pass
        node = last_child


def get_first_line_number(node):
    """
    From Python 3.8 onwards, lineno for decorated objects is the line at which
    the object definition starts, which is different from what Python < 3.8
    reported -- the lineno of the first decorator. To preserve this behaviour
    of Vulture for newer Python versions, which is also more accurate for
    counting the size of the unused code chunk (if the property is unused, we
    also don't need it's decorators), we return the lineno of the first
    decorator, if there are any.
    """
    if sys.version_info >= (3, 8):
        decorators = getattr(node, "decorator_list", [])
        if decorators:
            return decorators[0].lineno
    return node.lineno
