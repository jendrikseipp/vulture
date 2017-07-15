def _get_last_child(node):
    """
    Return the last direct child of `node`, or None if `node` has no children.

    We test all fields that contain lists of nodes, choose the last field
    that actually contains nodes and return the last node in the list.
    """
    reverse_ordered_fields = ['finalbody', 'orelse', 'handlers', 'body']
    for name in reverse_ordered_fields:
        last_children = getattr(node, name, [])
        if last_children:
            return last_children[-1]
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
