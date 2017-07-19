import ast


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
    ignored_fields = set(['ctx', 'decorator_list', 'names', 'returns'])
    for name in reversed(node._fields):
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
    while True:
        last_child = _get_last_child_with_lineno(node)
        if last_child is None:
            return node.lineno
        node = last_child


def count_lines(node):
    """
    Note: This function underestimates the size of code ending with multiline
    strings and comments.
    """
    return get_last_line_number(node) - node.lineno + 1
