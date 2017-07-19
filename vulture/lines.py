import ast


def _get_last_child(node):
    """
    Return the last direct child of `node`, or None if `node` has no children.

    We order the field names in the opposite order in which they appear
    in source code. Then we choose the first field (i.e., the field with
    the highest line number) that actually contains a node. If it
    contains a list of nodes, we return the last one.

    """
    reverse_ordered_fields = ['finalbody', 'orelse', 'handlers', 'body']
    for name in reverse_ordered_fields:
        try:
            last_field = getattr(node, name)
        except AttributeError:
            continue

        if isinstance(last_field, ast.AST):
            return last_field
        elif isinstance(last_field, list) and last_field:
            return last_field[-1]
    return None


def get_last_line_number(node):
    while True:
        last_child = _get_last_child(node)
        if last_child is None:
            return node.lineno
        node = last_child


def count_lines(node):
    """
    Note: This function underestimates the size of code ending with multiline
    statements and comments.
    """
    return get_last_line_number(node) - node.lineno + 1
