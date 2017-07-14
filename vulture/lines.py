def _get_last_child(node):
    fields = ['finalbody', 'orelse', 'handlers', 'body']
    for name in fields:
        try:
            field = getattr(node, name)
        except AttributeError:
            continue

        if isinstance(field, list):
            if field:
                return field[-1]
        else:
            return field
    return None


def get_last_line_number(node):
    while True:
        last_child = _get_last_child(node)
        if last_child is None:
            return node.lineno
        node = last_child


def count_lines(node):
    return get_last_line_number(node) - node.lineno + 1
