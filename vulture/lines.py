def get_last_line_number(node):
    return node.end_lineno


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
    decorators = getattr(node, "decorator_list", [])
    if decorators:
        return decorators[0].lineno
    return node.lineno
